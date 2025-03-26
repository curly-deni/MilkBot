class HybridDispatcher:

    def __init_subclass__(cls, *args, **kwargs):
        # print("Initializing hybrid dispatcher")

        deleting_func = []
        append_func = {}

        for func in cls.__dict__.values():
            if hasattr(func, "hybrid"):
                # print("Found hybrid function")
                deleting_func.append(func)

                for index, wrapped_func in enumerate(func()):
                    append_func[f"{func.__name__}_{index}"] = wrapped_func

        for func in deleting_func:
            delattr(cls, func.__name__)

        for name, func in append_func.items():
            # print(f"Adding function: {name}, {func}, type: {type(func)}")
            setattr(cls, name, func)

        super().__init_subclass__(*args, **kwargs)
