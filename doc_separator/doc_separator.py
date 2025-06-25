import os

input_dir = "./input/"
output_dir = "./output/"


def segment_lines(lines, min_length, max_length):
    segments = []
    segment = []
    segment_word_count = 0
    for i, line in enumerate(lines):
        segment.append(line)
        if '|' not in line:
            segment_word_count += len(line.split(" "))
        if segment_word_count >= max_length:
            print(f"Segment has {segment_word_count} words, which is greater than the maximum length of {max_length}.")
            print(f"At line {line}")
        if i == len(lines) - 1 or segment_word_count >= min_length:
            segments.append(segment)
            # 做重叠部分
            if len(segment[-1].split(' ')) > 20:
                segment = [segment[-1]]
            else:
                segment = segment[-2:]
            segment_word_count = 0
    return segments


def write_segmented_files(lines, f_name, min_length, max_length, title_line, nav_line):
    segments = segment_lines(lines, min_length, max_length)
    for i, segment in enumerate(segments):
        with open(output_dir + f"{f_name[:-3]}_{i}.md", "w", encoding="utf-8") as f_out:
            f_out.write(title_line)
            f_out.write(nav_line)
            for line in segment:
                f_out.write(line + '\n')


if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for file_name in os.listdir(input_dir):
    if file_name.endswith(".md"):
        with open(input_dir + file_name, "r", encoding="utf-8") as f:
            content = f.read()
            # 如果文件太短就直接输出
            if len(content.split(" ")) < 150:
                if len(content.split(" ")) < 80:
                    print(f"{file_name} is too short to be documented.")
                else:
                    print(f"{file_name} is too short to be segmented, but it will be documented anyway.")
                    with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as fo:
                        fo.write(content)
            else:
                content_lines = content.split("\n")
                title = ""
                nav = ""
                if content_lines[0].startswith("# "):
                    title = f'title: {content_lines[0][2:]}\n'
                if content_lines[1].startswith("**Navigation: "):
                    nav = f'navigation: {content_lines[1][3:-2]}\n'
                write_segmented_files(content_lines, file_name, 150, 250, title, nav)
