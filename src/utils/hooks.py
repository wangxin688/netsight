from typing import Any, Callable, List


def before_request(
    hook: Callable[[], Any] = None, only: List[str] = None
) -> Callable[..., Any]:
    """
    This decorator provides a way to hook into the request
    lifecycle by enqueueing methods to be invoked before each
    handler int the view. if the method returns a value other than:
    :code:`None`, then that value will be returned to the client.
    if Invoked with the :code: `only` kwargs, then hook will only be
    invoked for the given list of handler methods

    @cbv
    class SiteCBV:

        @before_request(only=["create", "update", "delete])
        def

    """
