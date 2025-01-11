import os
import multiprocessing

# Hàm kiểm tra nếu tên tệp chứa bất kỳ từ khóa nào
def check_file(filename, keywords):
    # Chuẩn hóa tên tệp thành chữ thường để so sánh không phân biệt chữ hoa/thường
    normalized_name = filename.lower()
    for keyword in keywords:
        if keyword in normalized_name:
            return filename
    return None

# Hàm xử lý cho từng tiến trình
def worker(files, folder_path, keywords):
    matches = []
    for file in files:
        result = check_file(file, keywords)
        if result:
            matches.append(os.path.join(folder_path, result))
    return matches

# Hàm chính để tìm kiếm và xóa các tệp không chứa từ khóa
def find_and_remove_files(folder_path, keywords, num_processes):
    # Lấy tất cả các tệp trong thư mục
    all_files = os.listdir(folder_path)

    # Chia danh sách tệp thành các phần nhỏ để xử lý song song
    chunk_size = len(all_files) // num_processes + 1
    file_chunks = [all_files[i:i + chunk_size] for i in range(0, len(all_files), chunk_size)]

    # Tạo pool đa tiến trình
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(worker, [(chunk, folder_path, keywords) for chunk in file_chunks])

    # Kết hợp kết quả từ tất cả các tiến trình
    matched_files = [file for sublist in results for file in sublist]

    # Xóa các tệp không khớp từ khóa
    matched_set = set(matched_files)
    for file in all_files:
        full_path = os.path.join(folder_path, file)
        if full_path not in matched_set:
            if os.path.isfile(full_path):  # Chỉ xóa nếu là tệp (file)
                os.remove(full_path)

    return matched_files

if __name__ == "__main__":
    # Thư mục cần quét
    folder_to_scan = '/home/user/downloads'

    # Các từ khóa cần tìm (chuẩn hóa thành chữ thường)
    keywords_to_search = ["ca", "hát", "tân cổ"]

    # Số tiến trình sử dụng
    num_processes = multiprocessing.cpu_count()

    # Tìm các tệp có chứa từ khóa và xóa tệp không phù hợp
    matching_files = find_and_remove_files(folder_to_scan, keywords_to_search, num_processes)

    # In kết quả
    print("Các tệp phù hợp:")
    for file in matching_files:
        print(file)

    # Đếm và in số lượng tệp phù hợp
    print(f"Tổng số tệp phù hợp: {len(matching_files)}")
