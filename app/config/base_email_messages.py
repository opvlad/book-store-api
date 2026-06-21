from app.models import Order


def get_base_message(
    template_name: str, user_name: str | None = None, order: Order | None = None
) -> str | None:
    match template_name:
        case "order_created":
            item_lines = []
            for item in order.items:
                parts = [f"{key}={value}" for key, value in item.items()]
                item_lines.append(f"<li>{', '.join(parts)}</li>")
            items = "\n".join(item_lines)

            return f"""
                <!DOCTYPE html>
                <html>
                <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6; max-width: 500px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #0056b3;">Order Confirmed! 🎉</h2>
                    <p>Hi {user_name},</p>
                    <p>Thanks for shopping with us! We've successfully received your order.</p>
                    <p><strong>Order #{order.id}:</strong>
                    <p><strong>Items:</strong></p>
                    <p><ol>{items}</ol></p>
                    <p><strong>Status:</strong> {order.status}</p>
                    <p><strong>Delivery type:</strong> {order.delivery_type}</p>
                    <p><strong>Total amount:</strong> ${order.total_amount}</p>
                </body>
                </html>
            """

        case _:
            return None
