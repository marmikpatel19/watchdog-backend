from uagents import Agent, Context, Model

class WeaponDetection(Model):
    filename: str

jerry = Agent(
    name="jerry",
    port=8001,
    seed="jerry's secret phrase",
    endpoint=["http://127.0.0.1:8001/submit"],
)

print(f"Jerry's address: {jerry.address}")

@jerry.on_message(model=WeaponDetection)
async def handle_weapon_detection(ctx: Context, sender: str, msg: WeaponDetection):
    ctx.logger.info(f"Weapon detected! Screenshot saved as {msg.filename}")

@jerry.on_interval(period=2.0)
async def search_for_weapon_or_suspect(ctx: Context):
    ctx.logger.info("Searching for weapon or suspect")

if __name__ == "__main__":
    jerry.run()