from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from django.apps import apps

# You can list all the model names whose changes should trigger cache invalidation.
CACHE_MODELS = [
    'Employee',
    'Department',
    'Task',
    'TaskFile',
    'User',
]


# Helper function
# Deletes all cache entries that start with the given prefix.
def invalidate_cache_by_prefix(prefix: str):
    # NOTE: Django’s default cache doesn’t support key prefix iteration,
    # so we store keys manually or use Redis with KEYS pattern matching if supported.
    # For now, we clear the entire cache to ensure consistency.
    # You can narrow this down later if you use Redis or similar backend.
    cache.clear()
    print(f"[Cache] Cleared due to change in {prefix}")


# This is invalidates cache when a TaskFile is uploaded.
@receiver(post_save)
def auto_invalidate_on_save(sender, instance, **kwargs):
    model_name = sender.__name__
    if model_name in CACHE_MODELS:
        invalidate_cache_by_prefix(model_name)

    if model_name == "TaskFile":
        invalidate_cache_by_prefix("TaskFileUpload")


# This invalidates cache when a task file is deleted.
@receiver(post_delete)
def auto_invalidate_on_delete(sender, instance, **kwargs):
    model_name = sender.__name__
    if model_name in CACHE_MODELS:
        invalidate_cache_by_prefix(model_name)

    if model_name == "TaskFile":
        invalidate_cache_by_prefix("TaskFileDelete")


# Invalidates cache when a many-to-many change is made.
@receiver(m2m_changed)
def auto_invalidate_on_m2m_change(sender, instance, **kwargs):
    model_name = instance.__class__.__name__
    if model_name in CACHE_MODELS:
        invalidate_cache_by_prefix(model_name)
