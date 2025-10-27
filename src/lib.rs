#![deny(
    elided_lifetimes_in_paths,
    explicit_outlives_requirements,
    keyword_idents,
    macro_use_extern_crate,
    meta_variable_misuse,
    missing_abi,
    missing_debug_implementations,
    non_ascii_idents,
    noop_method_call,
    single_use_lifetimes,
    trivial_casts,
    trivial_numeric_casts,
    unreachable_pub,
    unused_crate_dependencies,
    unused_extern_crates,
    unused_import_braces,
    unused_lifetimes,
    unused_qualifications,
    unused_results
)]

use pyo3::exceptions::PyValueError;
use pyo3::pybacked::PyBackedStr;
use pyo3::{
    prelude::*,
    types::{PyDict, PyList},
};

const MAGIC_MARKER: &str = "𒍟※";

fn is_magic_marker(value: &Bound<'_, PyAny>) -> bool {
    value
        .extract::<PyBackedStr>()
        .ok()
        .map(|s| <PyBackedStr as AsRef<str>>::as_ref(&s) == MAGIC_MARKER)
        .unwrap_or(false)
}

fn strip_marker_paths_in_list<'py>(
    list: &'py Bound<'py, PyList>,
    base_path: &str,
    removed_paths: &mut Vec<String>,
) -> PyResult<()> {
    for (index, value) in list.iter().enumerate() {
        let next_path = format!("{base_path}[{index}]");
        if let Ok(dict) = value.downcast::<PyDict>() {
            strip_marker_paths_in_dict(&dict, &next_path, removed_paths)?;
        } else if let Ok(sub_list) = value.downcast::<PyList>() {
            strip_marker_paths_in_list(&sub_list, &next_path, removed_paths)?;
        }
    }
    Ok(())
}

fn strip_marker_paths_in_dict<'py>(
    dict: &'py Bound<'py, PyDict>,
    base_path: &str,
    removed_paths: &mut Vec<String>,
) -> PyResult<()> {
    let py = dict.py();
    let mut keys_to_remove: Vec<Py<PyAny>> = Vec::new();
    for (key, value) in dict {
        let key_segment = key.str()?.to_str()?.to_owned();
        let next_path = format!("{base_path}.{key_segment}");
        if is_magic_marker(&value) {
            removed_paths.push(next_path);
            keys_to_remove.push(key.unbind());
            continue;
        }
        if let Ok(sub_dict) = value.downcast::<PyDict>() {
            strip_marker_paths_in_dict(&sub_dict, &next_path, removed_paths)?;
        } else if let Ok(sub_list) = value.downcast::<PyList>() {
            strip_marker_paths_in_list(&sub_list, &next_path, removed_paths)?;
        }
    }
    for key in keys_to_remove {
        dict.del_item(key.bind(py))?;
    }
    Ok(())
}

#[pyfunction]
fn strip_unmatched_markers<'py>(
    item: &'py Bound<'py, PyDict>,
) -> PyResult<&'py Bound<'py, PyDict>> {
    let mut removed_paths = Vec::new();
    strip_marker_paths_in_dict(item, "$", &mut removed_paths)?;
    if !removed_paths.is_empty() {
        let message = format!(
            "Stripped DO_NOT_MERGE_MARKER from: {}",
            removed_paths.join(", ")
        );
        let warnings = item.py().import("warnings")?;
        let _ = warnings.call_method1("warn", (message,))?;
    }
    Ok(item)
}

#[pyfunction]
#[pyo3(signature = (base, item, strip_unmatched_markers = false))]
fn hydrate<'py>(
    base: &'py Bound<'py, PyDict>,
    item: &'py Bound<'py, PyDict>,
    strip_unmatched_markers: bool,
) -> PyResult<&'py Bound<'py, PyDict>> {
    hydrate_dict(base, item)?;
    if strip_unmatched_markers {
        let _ = crate::strip_unmatched_markers(item)?;
    }
    Ok(item)
}

fn hydrate_any<'py>(base: &'py Bound<'py, PyAny>, item: &'py Bound<'py, PyAny>) -> PyResult<()> {
    if let Ok(item) = item.cast::<PyDict>() {
        if let Ok(base) = base.cast::<PyDict>() {
            hydrate_dict(base, item)?;
        } else if base.is_none() {
            hydrate_dict(&PyDict::new(base.py()), item)?;
        } else {
            return Err(PyValueError::new_err(
                "type mismatch: item is a dict, but the base was not",
            ));
        }
    } else if let Ok(item) = item.cast::<PyList>() {
        if let Ok(base) = base.cast::<PyList>() {
            hydrate_list(base, item)?;
        } else if base.is_none() {
            let empty_list: [&str; 0] = [];
            hydrate_list(&PyList::new(base.py(), &empty_list)?, item)?;
        } else {
            return Err(PyValueError::new_err(
                "type mismatch: item is a list, but base is not",
            ));
        }
    }
    Ok(())
}

fn hydrate_list<'py>(base: &'py Bound<'py, PyList>, item: &'py Bound<'py, PyList>) -> PyResult<()> {
    if base.len() == item.len() {
        for (base_value, item_value) in base.iter().zip(item.iter()) {
            hydrate_any(&base_value, &item_value)?;
        }
    }
    Ok(())
}

fn hydrate_dict<'py>(base: &'py Bound<'py, PyDict>, item: &'py Bound<'py, PyDict>) -> PyResult<()> {
    for (key, base_value) in base {
        if let Some(item_value) = item.get_item(&key)? {
            if item_value
                .extract::<PyBackedStr>()
                .ok()
                .map(|s| <PyBackedStr as AsRef<str>>::as_ref(&s) == MAGIC_MARKER)
                .unwrap_or(false)
            {
                item.del_item(key)?;
            } else {
                hydrate_any(&base_value, &item_value)?;
            }
        } else {
            item.set_item(key, base_value)?;
        }
    }
    Ok(())
}

#[pyfunction]
fn dehydrate<'py>(
    base: &'py Bound<'py, PyDict>,
    item: &'py Bound<'py, PyDict>,
) -> PyResult<&'py Bound<'py, PyDict>> {
    dehydrate_dict(base, item)?;
    Ok(item)
}

fn dehydrate_dict<'py>(
    base: &'py Bound<'py, PyDict>,
    item: &'py Bound<'py, PyDict>,
) -> PyResult<()> {
    for (key, base_value) in base {
        if let Some(item_value) = item.get_item(&key)? {
            if base_value.eq(&item_value)? {
                item.del_item(key)?;
            } else if let Ok(item_value) = item_value.cast::<PyList>() {
                if let Ok(base_value) = base_value.cast::<PyList>() {
                    dehydrate_list(base_value, item_value)?;
                }
            } else if let Ok(item_value) = item_value.cast::<PyDict>() {
                if let Ok(base_value) = base_value.cast::<PyDict>() {
                    dehydrate_dict(base_value, item_value)?;
                }
            }
        } else {
            item.set_item(key, MAGIC_MARKER)?;
        }
    }
    Ok(())
}

fn dehydrate_list<'py>(
    base: &'py Bound<'py, PyList>,
    item: &'py Bound<'py, PyList>,
) -> PyResult<()> {
    if base.len() == item.len() {
        for (base_value, item_value) in base.iter().zip(item.iter()) {
            if let Ok(base_value) = base_value.cast::<PyDict>() {
                if let Ok(item_value) = item_value.cast::<PyDict>() {
                    dehydrate_dict(base_value, item_value)?;
                }
            }
        }
    }
    Ok(())
}

#[pymodule]
fn hydraters(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("DO_NOT_MERGE_MARKER", MAGIC_MARKER)?;
    m.add_function(wrap_pyfunction!(crate::hydrate, m)?)?;
    m.add_function(wrap_pyfunction!(crate::dehydrate, m)?)?;
    m.add_function(wrap_pyfunction!(crate::strip_unmatched_markers, m)?)?;
    Ok(())
}
