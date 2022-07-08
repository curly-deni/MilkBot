def list_split(original_list) -> list[list]:
    return_list: list = []
    original_list_len_div_by_10: int = len(original_list) // 10
    for i in range(original_list_len_div_by_10 + 1):
        return_list.append(original_list[i * 10 : (i + 1) * 10])
    return return_list


def hex_to_rgb(hex: str) -> list[int]:
    rgb: list = []
    for i in (0, 2, 4):
        decimal: int = int(hex[i : i + 2], 16)
        rgb.append(decimal)
    return list(rgb)
