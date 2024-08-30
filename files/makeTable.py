# Jerrin Shirks

def makeTable(data,
              bold_row: int or list[int] = None,
              bold_col: int or list[int] = None,
              code: int or list[int] = None,
              sep: int or dict = None,
              show_index: bool = False,
              direction: int or str = 0,
              debug: bool = False) -> str:
    """
    :param data: a list of objects, lists, or other data.
    :param bold_row: real
    :param bold_col: real
    :param code: horizontal indexes of items that should be surrounded by ``.
    :param sep: dict of horizontal indexes with str's to separate args.
    :param show_index: a bool that adds an index to the first item if true.
    :param direction: justifies or centers text in code blocks this direction.
    :param debug: prints stuff to terminal
    :return: A table of all represented data parsed with above arguments.
    """

    # parsing data
    if data is []:
        return ""
    if not isinstance(data, list):
        data = [data]

    # parsing boldRow
    if bold_row is None:
        bold_row = []
    if isinstance(bold_row, int):
        bold_row = [bold_row]

    # parsing boldCol
    if bold_col is None:
        bold_col = []
    if isinstance(bold_col, int):
        bold_col = [bold_col]

    # parsing code
    if code is None:
        code = []
    if isinstance(code, int):
        code = [code]

    # parsing sep arg
    if sep is None:
        sep = {}
    if isinstance(sep, int):
        sep = [sep]

    # 0: right, 1: left, 2: center
    # parsing direction arg
    if isinstance(direction, str):
        if direction.lower() in ["r", "right"]:
            direction = 0
        elif direction.lower() in ["l", "left"]:
            direction = 1
        elif direction.lower() in ["c", "center"]:
            direction = 2
    elif not isinstance(direction, int):
        direction = 0

    # step 1
    # make sure that every item in the data is a list
    # also get the longest list in data
    max_size = 0
    for index, item in enumerate(data):
        if type(item) == tuple:
            item = list(item)

        if isinstance(item, list):
            size = len(item)
        else:
            item = [item]
            size = 0

        if size > max_size:
            max_size = size

        data[index] = item

    # step 2
    # make sure every item in data is the same length
    show_index_length = len(str(len(data)))
    if show_index:
        max_size += 1
        code = [i + 1 for i in code]
        code.insert(0, 0)

    for index, item in enumerate(data):
        if show_index:
            item.insert(0, f"{index + 1}.".rjust(show_index_length))

        if len(item) < max_size:
            to_add = max_size - len(item)
            data[index].extend([None] * to_add)

    # step 3
    # this gets the longest items per vertical index
    line_segments = len(data[0])
    max_length_list = []

    for index in range(line_segments):
        max_length = 0

        for item in range(len(data)):
            if data[item][index] is None:
                continue

            length: int = len(str(data[item][index]))
            if length > max_length:
                max_length = length

        max_length_list.append(max_length)

    # step 3.5
    if debug:
        for i in data:
            print(i)
        print("lengths", max_length_list)
        print("boxed", code)
        input()

    # final step 4
    final_string = []
    for index, item in enumerate(data, start=0):
        string: str = ""

        is_code_block = False

        # add each segment
        for seg_index in range(max_size):
            seg_part = ""

            segment = data[index][seg_index]

            if segment is None:
                segment = ""

            # if current is NOT block and last is block <3
            elif not is_code_block and seg_index in code:
                seg_part += "``"

            is_code_block = seg_index in code

            # add the main part of the string
            if direction == 0:  # right
                seg_part += f"{str(segment).rjust(max_length_list[seg_index])}"
            elif direction == 1:  # left
                seg_part += f"{str(segment).ljust(max_length_list[seg_index])}"
            elif direction == 2:  # center
                seg_part += f"{str(segment).center(max_length_list[seg_index])}"

            # add if this is code block but next isn't, finishing it
            if seg_index in code and seg_index + 1 not in code:
                seg_part += "``"

            # vertical bold
            if seg_index in bold_col:
                seg_part = f"**{seg_part}**"

            string += seg_part

            # add the spacer
            if seg_index < line_segments:

                if seg_index in sep:
                    if data[index][seg_index + 1] is None:
                        string += " " * len(sep[seg_index])
                    else:
                        string += f"{sep[seg_index]}"
                else:
                    string += " "

        if index in bold_row:
            string = f"**{string}**"

        final_string.append(string)

    text = "\n".join(final_string)
    return text
