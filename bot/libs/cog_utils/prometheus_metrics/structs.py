import msgspec
from prometheus_client import Counter, Gauge


class GuildMetrics(msgspec.Struct):
    text: int
    voice: int
    guilds: int
    total_members: int
    total_unique_members: int
    total_commands: int


class Metrics(msgspec.Struct):
    connection_gauge: Gauge
    latency_gauge: Gauge
    on_app_command_counter: Counter
    guild_gauge: Gauge
    text_channel_gauge: Gauge
    voice_channel_gauge: Gauge
    user_gauge: Gauge
    user_unique_gauge: Gauge
    commands_gauge: Gauge
