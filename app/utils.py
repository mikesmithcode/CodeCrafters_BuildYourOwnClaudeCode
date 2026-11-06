import functools
import os

def debug_trace(func):
    """Universal decorator to log entry, args, returns, and errors using the DEBUG environment variable."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check the environment variable directly
        is_debug = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")

        if is_debug:
            print(f"\n[DEBUG ENTER] ──> {func.__name__}()")
            
            # Optional: Cleanly hide 'self' if the first argument is an object instance
            logged_args = args[1:] if args and hasattr(args[0], "__dict__") else args
            
            if logged_args:
                print(f"  Args: {logged_args}")
            if kwargs:
                print(f"  Kwargs: {kwargs}")

        try:
            result = func(*args, **kwargs)
            if is_debug:
                print(f"\n[DEBUG EXIT] <── {func.__name__}() completed successfully")
                if result is not None:
                    print(f"  Result preview: {str(result)[:120]}...")
            return result
        except Exception as e:
            if is_debug:
                print(f"[DEBUG ERROR] <!! {func.__name__}() raised {type(e).__name__}: {e}")
            raise
            
    return wrapper

def debug_agent(func):
    """Specialized decorator for tracking class instantiation and method lifecycles."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        is_debug = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")
        
        # Extract class name if it's a method
        class_name = args[0].__class__.__name__ if args else "Unknown"
        
        if is_debug:
            if func.__name__ == "__init__":
                print(f"\n[AGENT SPAWN] ──> Initializing new {class_name} instance")
            else:
                print(f"\n[DEBUG ENTER] ──> {class_name}.{func.__name__}()")
                
            logged_args = args[1:] if args and hasattr(args[0], "__dict__") else args
            if logged_args:
                print(f"  Args: {logged_args}")
            if kwargs:
                print(f"  Kwargs: {kwargs}")

        try:
            result = func(*args, **kwargs)
            if is_debug:
                if func.__name__ == "__init__":
                    print(f"[AGENT READY] <── {class_name} instance ready")
                else:
                    print(f"[DEBUG EXIT] <── {class_name}.{func.__name__}() completed")
                    if result is not None:
                        print(f"  Result preview: {str(result)[:120]}...")
            return result
        except Exception as e:
            if is_debug:
                print(f"[DEBUG ERROR] <!! {class_name}.{func.__name__}() raised {type(e).__name__}: {e}")
            raise
            
    return wrapper