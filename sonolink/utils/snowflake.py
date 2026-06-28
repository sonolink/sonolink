from typing import Protocol, runtime_checkable


@runtime_checkable
class Snowflake(Protocol):
    """Represents a Discord Snowflake, which is a unique identifier used for various entities in Discord.

    This may be represented as Message, User, Channel, etc. objects that have an `id` attribute.

    Attributes
    ----------
    id: :class:`int`
        The snowflake ID as an integer.

    """

    id: int
