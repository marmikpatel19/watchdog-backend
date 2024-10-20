from uagents import Agent, Context, Model
import geocoder

class CoordinateMessage(Model):
    latitude: float
    longitude: float

# Replace this with Jerry's actual address when you have it
JERRY_ADDRESS = "agent1qv6m8vp5hq45xhvtjnuxv9ksr2cffnxlfgq4tncnq8r2l0vu260c8tvxnz"

tom = Agent(
    name="tom",
    port=8000,
    seed="tom's secret phrase",
    endpoint=["http://127.0.0.1:8000/submit"],
)

print(f"Tom's address: {tom.address}")

@tom.on_interval(period=2.0)
async def send_coordinates(ctx: Context):
    g = geocoder.ip('me')
    if g.ok:
        coordinates = CoordinateMessage(latitude=g.lat, longitude=g.lng)
        await ctx.send(JERRY_ADDRESS, coordinates)
        ctx.logger.info(f"Sent coordinates to Jerry: {coordinates}")
    else:
        ctx.logger.info("Failed to get coordinates")

@tom.on_message(model=CoordinateMessage)
async def message_handler(ctx: Context, sender: str, msg: CoordinateMessage):
    ctx.logger.info(f"Received message from {sender}: Lat: {msg.latitude}, Long: {msg.longitude}")

if __name__ == "__main__":
    tom.run()