import os
import subprocess
import shutil


def move_files_to_total(source_dir, total_dir):
    # 确保目标目录total存在
    if not os.path.exists(total_dir):
        os.makedirs(total_dir)

    # 递归遍历源目录
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            source_file_path = os.path.join(root, file)
            destination_file_path = os.path.join(total_dir, file)

            # 如果目标文件已经存在，重新命名以避免冲突
            if os.path.exists(destination_file_path):
                base, extension = os.path.splitext(file)
                i = 1
                new_file_name = f"{base}_{i}{extension}"
                destination_file_path = os.path.join(total_dir, new_file_name)
                while os.path.exists(destination_file_path):
                    i += 1
                    new_file_name = f"{base}_{i}{extension}"
                    destination_file_path = os.path.join(total_dir, new_file_name)

            # 复制文件
            shutil.copy2(source_file_path, destination_file_path)
            print(f"移动文件: {source_file_path} 到 {destination_file_path}")


def compress_images(input_dir, output_dir, quality=75):
    # 检查输入和输出目录是否存在
    if not os.path.exists(input_dir):
        raise Exception(f"Input directory {input_dir} does not exist.")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取输入目录中的所有文件
    files = os.listdir(input_dir)
    for file in files:
        input_file = os.path.join(input_dir, file)
        temp_output_file = os.path.join(output_dir, "temp_" + file)
        final_output_file = os.path.join(output_dir, file)

        # 检查是否为文件而非子目录
        if os.path.isfile(input_file):
            # 使用 zsh -c 来加载 nvm 并调用 squoosh-cli 压缩文件到临时文件
            cmd = f"""
            zsh -c '
            source ~/.zshrc
            nvm use v12.22.12
            squoosh-cli {input_file} -d {temp_output_file} --webp {{"quality":{quality}}}
            '
            """
            try:
                subprocess.run(cmd, shell=True, check=True, executable="/bin/zsh")

                # 检查压缩后的文件大小
                original_size = os.path.getsize(input_file)
                compressed_size = os.path.getsize(temp_output_file)

                if compressed_size < original_size:
                    # 如果压缩后文件更小，替换最终输出文件
                    shutil.move(temp_output_file, final_output_file)
                    print(f"Compressed {input_file} to {final_output_file}")
                else:
                    # 如果压缩后文件更大，删除临时文件并输出提示
                    os.remove(temp_output_file)
                    print(f"Skipped {input_file}: compressed file is larger than the original.")

            except subprocess.CalledProcessError as e:
                print(f"Error compressing {input_file}: {e}")
    move_files_to_total(output_dir, all_compressed_files_dir)


if __name__ == "__main__":
    input_directory = "/Users/chenjianxiang/Downloads/input"
    output_directory = "/Users/chenjianxiang/Downloads/output"
    all_compressed_files_dir = "/Users/chenjianxiang/Downloads/all_compressed_files"
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
    if os.path.exists(all_compressed_files_dir):
        shutil.rmtree(all_compressed_files_dir)
    if os.path.exists(input_directory):
        compress_images(input_directory, output_directory)
