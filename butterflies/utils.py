"""
Utilities for display formatting and common functions in the butterflies app.
"""
from django.http import Http404


def get_model_by_name(model_name, model_list_func):
    """
    Helper function to get a model by its name from the model_list.
    Raises Http404 if the model is not found.
    Args:
        model_name: String name of the model to find
        model_list_func: Function that returns a list of model classes
    Returns:
        The model class if found, otherwise raises Http404.
    """
    model = None
    for m in model_list_func():
        if m._meta.model_name == model_name:
            model = m
            break
    if not model:
        raise Http404("Model not found")
    return model
    # Helper function to get a model by its name from the model_list.
    # Raises Http404 if the model is not found.
    # Args:
    #     model_name: String name of the model to find
    #     model_list_func: Function that returns a list of model classes
    # Returns:
    #     The model class if found, otherwise raises Http404.
