from django import template

register = template.Library()

@register.filter()
def indian_currency(value):
    try:
        value = float(value)
    except:
        return value
    
    # split parts (integer and decimal)
    value = f'{value:.2f}'
    parts = value.split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    # Handle Indian number format for integer part
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        rest = integer_part[:-3]
        formatted = ""
        while len(rest) > 2:
            formatted = "," + rest[-2:] + formatted
            rest = rest[:-2]
        formatted = rest + formatted + "," + last_three if rest else last_three
    else:
        formatted = integer_part

    return f"₹{formatted}.{decimal_part}"


@register.filter()
def stock_number(value):
    try:
        return float(value.split()[0]) 
    except (ValueError, IndexError):
        return 0
