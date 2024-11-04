from itertools import product
from collections import defaultdict
from itertools import combinations

def find_unique_combinations(lists):
    unique_lists = [list(set(lst)) for lst in lists]
    all_combinations = list(product(*unique_lists))
    unique_combinations = [list(combo) for combo in all_combinations if len(combo) == len(set(combo))]
    return unique_combinations

def merge_same_list(lists):
    # 使用字典来记录每个集合对应的列表索引
    set_to_indices = defaultdict(list)
    for index, lst in enumerate(lists):
        # 将列表转换为集合并排序以确保顺序一致
        set_representation = tuple(sorted(set(lst)))
        set_to_indices[set_representation].append(index)

    # 根据等价关系合并列表
    merged_lists = []
    for indices in set_to_indices.values():
        if len(indices) > 1:
            # 如果有多个列表包含相同的元素，则合并它们
            merged_list = lists[indices[0]]
            for i in indices[1:]:
                # 验证所有列表是否真的包含相同的元素
                if set(lists[i]) == set(merged_list):
                    merged_list = merged_list  # 合并逻辑，这里因为元素相同所以直接使用第一个列表
            merged_lists.append(merged_list)
        else:
            # 如果只有一个列表包含这些元素，则直接添加
            merged_lists.append(lists[indices[0]])

    return merged_lists

def get_rules_comb(lists):
    lists_ends = [lists[:-1] + [list_end] for list_end in lists[-1]]
    # print(lists_ends)

    res = []
    for list_end in lists_ends:
        combs = find_unique_combinations(list_end[:-1])
        combs_merge = merge_same_list(combs)
        for comb_merge in combs_merge:
            if list_end[-1] not in comb_merge:
                res.append(comb_merge + [list_end[-1]])
    
    return res

def get_all_combinations(n, b):
    sequence = range(n)
    all_combinations = list(combinations(sequence, b))
    all_combinations = [list(combination) for combination in all_combinations]
    return all_combinations

def comb_same_lines(labels, count):
    row_merge_ids = []

    last_labels = []
    last_counts = []
    # print(labels)

    ct = -1
    for sj, label in enumerate(labels):
        # 检查当前行是否和历史行有重复
        repeat_id = -1
        for i, last_label in enumerate(last_labels):
            if all([x == y for x, y in zip(last_label, label)]):
                repeat_id = i
                break
        
        if repeat_id == -1:
            ct += 1
            row_merge_ids.append(ct)
            try:
                last_labels.append(label.tolist())
            except:
                last_labels.append(label)
            last_counts.append(count[sj])

        else:
            last_counts[repeat_id] += count[sj]
            row_merge_ids.append(row_merge_ids[last_labels.index(label.tolist())])

    # print(row_merge_ids, last_counts)
    return last_labels, last_counts

def get_2dlist_print(data, head=''):
    col_widths = [max(len(str(item)) for item in column) for column in zip(*data)]

    res = ''
    for row in data:
        res += head + "   ".join("{:<{}}".format(item, width) for item, width in zip(row, col_widths)) + '\n'

    return res




if __name__ == '__main__':
    # lists = [[0, 1, 2, 3], [0, 1, 2, 3], [1], [0, 1, 2, 3]]
    lists = [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1]]
    list_res = get_rules_comb(lists)

    # 输出结果为从lists除掉最后一个前面的列表中排列组合选择出不重复的情况然后对应到lists最后一个输出
    # 因为lists除掉最后一个的前面是输入，是无序的，因此就算顺序不同包含元素相同也要合并
    for res in list_res:
        print(res)