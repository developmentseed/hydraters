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

#[pyfunction]
fn hydrate<'py>(
    base: &'py Bound<'py, PyDict>,
    item: &'py Bound<'py, PyDict>,
) -> PyResult<&'py Bound<'py, PyDict>> {
    hydrate_dict(base, item)?;
    Ok(item)
}

fn hydrate_any<'py>(base: &'py Bound<'py, PyAny>, item: &'py Bound<'py, PyAny>) -> PyResult<()> {
    if let Ok(item) = item.downcast::<PyDict>() {
        if let Ok(base) = base.downcast::<PyDict>() {
            hydrate_dict(base, item)?;
        } else {
            return Err(PyValueError::new_err(
                "type mismatch: item is a dict, but the base was not",
            ));
        }
    } else if let Ok(item) = item.downcast::<PyList>() {
        if let Ok(base) = base.downcast::<PyList>() {
            hydrate_list(base, item)?;
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
            } else if let Ok(item_value) = item_value.downcast::<PyList>() {
                if let Ok(base_value) = base_value.downcast::<PyList>() {
                    dehydrate_list(base_value, item_value)?;
                }
            } else if let Ok(item_value) = item_value.downcast::<PyDict>() {
                if let Ok(base_value) = base_value.downcast::<PyDict>() {
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
            if let Ok(base_value) = base_value.downcast::<PyDict>() {
                if let Ok(item_value) = item_value.downcast::<PyDict>() {
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
    Ok(())
}
