import numpy as np
import os
from anytree import Node, RenderTree
from utils import get_all_combinations, comb_same_lines, get_2dlist_print

class AssociationRulesSolve():

    def __init__(self, 
                 cols=6,        # 表格列数    
                 data_path='',  # 表格数据地址
                 data=[]# 也可以选择输入数据的模式初始化
                 ):
        # 所有应该输出的信息
        self.info = ''
        # 数据初始化
        self.cols = cols
        # if not os.path.exists(data_path):
        #     print('数据未找到！')
        #     return
        
        if os.path.exists(data_path):
            lines = []
            with open(data_path, 'r') as file:
                for line in file:
                    # 使用rstrip('\n')去除行尾的换行符
                    lines.append(line.rstrip('\n'))

            data = np.array(lines).reshape(cols, -1)

        elif len(data):
            print('使用输入数据初始化')
            data = np.array(data).reshape(cols, -1)
            # for i in range(1, data.shape[1]):
            #     data[-1][i] = int(data[-1][i])
        else:
            print('数据未找到！')
            self.success = 0
        self.rows = data.shape[1]
        self.data = []
        for i in range(data.shape[0]-1):
            self.data.append(data[i][1:].tolist())

        self.data.append(data[-1][1:].astype('int').tolist())
        self.heads = data[:, 0].tolist()
        print(self.data)
        print(self.heads)
        self.data_num = np.sum(data[-1, 1:].astype('int'))  # 数据总量


        self.tree = []
        
        self.success = 1
    def solveQ1(self, 
                s_th=0.25,     # 最小支持度阈值
                c_th=0.5,      # 最小置信度阈值
                SAR_id=0,      # 要求的强关联规则输出的列对应id
                SAR_deg=2,     # 解频繁n项集 
                ):
        self.info = ''
        self.s_th = s_th
        self.c_th = c_th
        self.SAR_id = SAR_id
        self.SAR_deg = SAR_deg

        self.data_poped = [dt for isml, dt in enumerate(self.data) if isml != SAR_id]
        # print(self.data_poped)
        self.support_num = s_th * self.data_num             # 最小支持数

        self.info += f'样本总数={self.data_num}\n'
        self.info += f'最小支持数={round(self.support_num, 4)}\n'

        # 遍历拆解SAR_id对应的值
        self.info += f'分别讨论 {self.heads[SAR_id]} 取不同值的情况\n'
        SAR_types = list(set(self.data[SAR_id]))
        # print(SAR_types)
        selected_segs = []
        for sar_i, sar_t in enumerate(SAR_types):

            self.info += f'\n({sar_i + 1}) {self.heads[SAR_id]} = {sar_t}\n'
            last_labels, last_counts = self.seperate_keys(self.heads[SAR_id], sar_t, self.data, self.heads)

            last_labels_ar = np.array(last_labels).T
            last_counts_ar = np.array([last_counts]).astype('str').T
            heads_now = np.array([[head for i, head in enumerate(self.heads) if i != self.SAR_id]])
            # print(np.array([self.heads]).shape, last_counts_ar.shape)
            last_data_ar = np.hstack((last_labels_ar.T, last_counts_ar))
            last_data_ar = np.vstack((heads_now, last_data_ar))
            self.info += '\n' + get_2dlist_print(last_data_ar, head='  ') + '\n'

            # 求解频繁n项集
            segs_all = []
            for od in range(self.SAR_deg):
                segs = []
                selections = get_all_combinations(last_labels_ar.shape[0], od + 1)

            #     # print(selections)
                # print(f'频繁{od + 1}项集：')
                for sec in selections:
                    label_now = [last_labels_ar[sec_id].tolist() for sec_id in sec]
                    label_now, count_now = comb_same_lines(np.array(label_now).T, last_counts)
                    # 
                    # data_selected = [data_poped[sdm] for sdm in sec]
                    data_selected = [self.data_poped[sdm] for sdm in sec]
                    data_selected = np.array(data_selected).T
                    
                    for i, l in enumerate(label_now):
                        if count_now[i] >= self.support_num:
                            c_dem = 0 # 置信度分母
                            for ii, dsl in enumerate(data_selected):

                                if all([x == y for x, y in zip(dsl, l)]):
                                    c_dem += self.data[-1][ii]
                            if c_dem:
                                segs.append([sec, l, count_now[i], count_now[i] / self.data_num, count_now[i] / c_dem, c_dem])
                            else:
                                segs.append([sec, l, count_now[i], count_now[i] / self.data_num, 0, c_dem])

                            # print(data_selected)
                            # print(sec, l, count_now[i], c_dem)

                segs_all.append(segs)

            for i, segs in enumerate(segs_all):
                if not segs:
                    self.info += f'  未找到频繁{i+1}项集\n'
                    break

                if i == 0:
                    self.info += f'  频繁{i+1}项集:\n' + '  L1={\n'
                    for select, labels, ni, s, c, c_dem in segs:
                        # sl_names = [self.heads[ssli] for ssli in select]
                        sl_names = [heads_now[0][ssli] for ssli in select]
                        ssl = np.array([sl_names, ['=' for ssli in range(len(select))], labels]).T.tolist()
                        for i in range(len(ssl)):
                            ssl[i] = ''.join(ssl[i])

                        ssl = ','.join(ssl)
                        self.info += f'    {ssl}:{ni},\n'

                    self.info += '  }\n'

                else:
                    self.info += f'  频繁{i+1}项集的待选集:\n  C{i+1}=' + '{\n'
                    for select, labels, ni, s, c, c_dem in segs:
                        # sl_names = [self.heads[ssli] for ssli in select]
                        sl_names = [heads_now[0][ssli] for ssli in select]
                        ssl = np.array([sl_names, ['=' for ssli in range(len(select))], labels]).T.tolist()
                        for i in range(len(ssl)):
                            ssl[i] = ''.join(ssl[i])

                        ssl = '('+', '.join(ssl)+')'
                        self.info += f'    {ssl}: {ni},\n'

                    self.info += '  }\n'

                    self.info += f'  计算频繁{i+1}项集置信度：\n'
                    for (select, labels, ni, s, c, c_dem) in segs:
                        # if s < self.s_th or c < self.c_th:
                            # continue

                        # sl_names = [self.heads[ssli] for ssli in select]
                        sl_names = [heads_now[0][ssli] for ssli in select]
                        ssl = np.array([sl_names, 
                                        ['(S, ' for ssli in range(len(select))],
                                        labels,
                                        [')' for ssli in range(len(select))]
                                        ],).T.tolist()
                        for i in range(len(ssl)):
                            ssl[i] = ''.join(ssl[i])

                        ssl = ' ^ '.join(ssl)
                        nsk = f'  {ssl} => {self.heads[self.SAR_id]}(S, {sar_t}) [s={ni}/{self.data_num}={round(s*100, 4)}%, c={ni}/{c_dem}={round(c*100, 4)}%]\n'
                        self.info += nsk
                        if i == SAR_deg-1 and s >= self.s_th and c >= self.c_th:
                            # print(i)
                            selected_segs.append(nsk)

                    segs_filtered = [(select, labels, ni, s, c, c_dem) for (select, labels, ni, s, c, c_dem) in segs if s >= self.s_th and c >= self.c_th]
                    
                    if not segs_filtered:
                        self.info += f'  未找到频繁{i+1}项集\n'
                        break


                    self.info += f'  频繁{i+1}项集:\n  L{i+1}=' + '{\n'
                    

                    for select, labels, ni, s, c, c_dem in segs_filtered:
                        # if s < self.s_th or c < self.c_th:
                        #     continue
                        sl_names = [self.heads[ssli] for ssli in select]
                        ssl = np.array([sl_names, ['=' for ssli in range(len(select))], labels]).T.tolist()
                        for i in range(len(ssl)):
                            ssl[i] = ''.join(ssl[i])

                        ssl = '('+', '.join(ssl)+')'
                        self.info += f'    {ssl}: {ni},\n'

                    self.info += '  }\n'

        if selected_segs:
            self.info += '\n因此，所有强关联规则为：\n' + ''.join(selected_segs)
        else:
            self.info += '\n未找到符合要求的强关联规则！\n'
        self.selected_segs = selected_segs
        # print(selected_segs)
        return self.info

    # 选中表头的项提取出其对应的表格
    def seperate_keys(self, head, value, data, heads):
        head_id = heads.index(head)
        rows_selected = [i for i, v in enumerate(data[head_id]) if v == value]
        head_selected = [h for h in heads if h != head]
        data_selected = []
        for i in range(len(data)):
            if i == head_id:
                continue
            data_selected.append([data[i][j] for j in range(len(data[0])) if j in rows_selected])

        # print(head_selected, data_selected)

        # 合并相同行
        labels = np.array(data_selected[:-1]).T
        count = data_selected[-1]

        return comb_same_lines(labels, count)

    def get_max_G(self, DTR_id=0):# 判定树根节点对应列数
        self.info = ''
        # print(self.data[DTR_id])
        last_labels_ar = np.array([self.data[DTR_id]]).T
        last_counts_ar = np.array([self.data[-1]]).T
        self.info += '计算整体信息量：\n'
        last_labels_ar, last_counts_ar = comb_same_lines(last_labels_ar, last_counts_ar)
        last_freq = last_counts_ar / self.data_num
        last_freq = np.round(last_freq, 4)
        total_ar = np.array([['Total', self.data_num, 1.0]]).T
        # now_exel = np.vstack((np.hstack((np.array([['Count', 'Frequency']]).T, last_labels_ar, last_counts_ar, last_freq)), total_ar))
        now_exel = np.hstack((np.array([['', 'Count', 'Frequency']]).T, np.hstack((last_labels_ar, last_counts_ar, last_freq)).T, total_ar))
        self.info += '\n' + get_2dlist_print(now_exel, head='') + '\n'
        # 计算整体信息增益
        # I_all = -np.sum(np.log2(last_freq) * last_freq)
        I_all_total = [- np.log2(last_freq[i]) * last_freq[i] if last_freq[i] else 0 for i in range(last_freq.shape[0])]
        I_all_total = sum(I_all_total)[0]
        count_str = [str(lca[0]) for lca in  last_counts_ar]
        Ixs = ','.join(count_str)
        # print(np.array(last_counts_ar).T.tolist()[0])
        self.info += f'I({Ixs}) = -Σpi*log_2(pi) = {round(I_all_total, 4)}\n'

        # 计算各个信息增益
        G_all = []
        G_all_ids = []
        DTR_types = list(set(self.data[DTR_id]))
        for i in range(len(self.heads) - 1):
            if i == DTR_id:
                continue
            now_types = list(set(self.data[i]))
            

            data_mat_now = np.zeros((len(DTR_types), len(now_types)))
            for jms in range(len(self.data[0])):
                now_label = self.data[i][jms]
                data_mat_now[DTR_types.index(self.data[DTR_id][jms]), now_types.index(now_label)] += self.data[-1][jms]

            data_mat_now = data_mat_now.T.astype('int')
            # now_show_mat = 
            # print(self.heads[i])
            # print(np.array([[self.heads[i]]+now_types+['Total']]).T)
            # print(np.array([DTR_types+['Total']]))
            # print(data_mat_now)
            # print(np.append(np.sum(data_mat_now, axis=0), self.data_num).reshape(1,-1), np.sum(data_mat_now, axis=1).reshape(-1,1))
            

            res_mat_now =  np.hstack((
                        np.array([[self.heads[i]]+now_types+['Total']]).T,
                        np.vstack((np.array([DTR_types+['Total']]),
                        np.hstack((data_mat_now, np.sum(data_mat_now, axis=1).reshape(-1,1))),
                        np.append(np.sum(data_mat_now, axis=0), int(self.data_num)).reshape(1,-1)))
            ))
            
            self.info += f'\n计算{self.heads[i]}属性信息增益：\n'
            self.info += '\n' + get_2dlist_print(res_mat_now, head='  ') + '\n'
            I_now_all = []
            for i_id_og in data_mat_now:
                i_id = i_id_og / np.sum(i_id_og)
                I_all = sum([- np.log2(i_id[i]) * i_id[i] if i_id[i] else 0 for i in range(i_id.shape[0])])
                I_now_all.append(I_all)

            E_now = np.sum(np.sum(data_mat_now, axis=1) / self.data_num * np.array(I_now_all))
            # print(E_now)
            
            E_print_str_lst = []
            for iee in range(len(I_now_all)):
                I_xs = ','.join(data_mat_now[iee].astype('int').astype('str').tolist())
                E_print_str_lst.append(f'{int(float(res_mat_now[iee+1][-1]))}/{self.data_num}*I({I_xs})')

            E_result_lst = []
            for iee in range(len(I_now_all)):
                E_result_lst.append(f'{round(float(res_mat_now[iee+1][-1])/self.data_num, 4)}*{round(I_now_all[iee], 4)}')
            # print('+'.join(E_print_str_lst))
            self.info += f'E({self.heads[i]}) = '+'+'.join(E_print_str_lst)+'\n = '+'+'.join(E_result_lst)+'\n = '+str(round(E_now, 4))+'\n'

            gain_now = I_all_total - E_now
            self.info += f'Gain({self.heads[i]}) = I({Ixs})-E({self.heads[i]}) = '+str(round(gain_now, 4))+'\n'
            G_all.append(gain_now)
            G_all_ids.append(i)
            # break

        self.G_all = G_all
        self.G_all_ids = G_all_ids
        print(G_all, G_all_ids)


    def solveQ2_1(self, DTR_id=2):
        self.get_max_G(DTR_id=DTR_id)
        max_G_id = self.G_all_ids[self.G_all.index(max(self.G_all))]
        
        max_G_types = list(set(self.data[max_G_id]))
        print(self.heads[max_G_id])

        head_now = self.heads.copy()
        head_now.pop(max_G_id)
        print(head_now)
        for sar_i, sar_t in enumerate(max_G_types):
            last_labels, last_counts = self.seperate_keys(self.heads[max_G_id], sar_t, self.data, self.heads)

            data_now = last_labels + [last_counts]
            print(data_now)
            
        
        return self.info    
    
    def solveQ2_2(self, data, heads, DTR_id=2, parent='', recursion_num=0):
        
        smallq2 = SmallQ2(data, heads)
        smallq2.get_max_G(DTR_id=DTR_id)
        max_G_id = smallq2.G_all_ids[smallq2.G_all.index(max(smallq2.G_all))]
        
        max_G_types = list(set(smallq2.data[max_G_id]))
        print('信息增益最大的列：', smallq2.heads[max_G_id], max(smallq2.G_all))
        self.info += '\n  '*recursion_num + f'{smallq2.heads[max_G_id]} 信息增益最大，Gain({smallq2.heads[max_G_id]}) = {round(max(smallq2.G_all), 4)}\n'
        head_now = smallq2.heads.copy()
        head_now.pop(max_G_id)
        
        if not parent:
            node_max = Node(smallq2.heads[max_G_id])
            self.root_node = node_max
        else:
            node_max = Node(smallq2.heads[max_G_id], parent=parent)
        self.tree.append(node_max)

        now_DTR_id = head_now.index(heads[DTR_id])
        print("headnow", head_now, now_DTR_id)
        for sar_i, sar_t in enumerate(max_G_types):
            print(f'--取{smallq2.heads[max_G_id]}={sar_t}')
            self.info += '  '*recursion_num + f'({sar_i+1}) {smallq2.heads[max_G_id]}={sar_t}\n'
        
            # target_node = anytree.find(self.tree[0], filter_=lambda node: node.name == node_max)
            new_child = Node(sar_t, parent=node_max)
            self.tree.append(new_child)

            last_labels, last_counts = smallq2.seperate_keys(smallq2.heads[max_G_id], sar_t, smallq2.data, smallq2.heads)
            
            last_labels, last_counts = comb_same_lines(np.array(last_labels), last_counts)
            last_labels = np.array(last_labels).T.tolist()
            data_now = last_labels + [last_counts]
            print("head_now", head_now, "data_now", data_now)
            

            # print(list(set(data_now[now_DTR_id])))
            # 添加矩阵显示

            # print_data_now = np.array(data_now).T
            print_data_now = np.vstack((np.array([head_now]), np.array(data_now).T))

            # print(print_data_now, np.array([head_now]))
            self.info += '\n' + get_2dlist_print(print_data_now, head='  '+'  '*recursion_num) + '\n'


            merge_dtr_col = list(set(data_now[now_DTR_id]))
            if len(merge_dtr_col) == 1:
                node_now = Node(merge_dtr_col[0], parent=new_child) 
                self.tree.append(node_now) 
                self.info += '  '*recursion_num + f'  此时{head_now[now_DTR_id]}只有一个取值，故取 {head_now[now_DTR_id]}={merge_dtr_col[0]}，停止分割\n'  
                print('搜索到头了')
                continue

            if len(head_now) == 3:
                now_name = data_now[now_DTR_id][data_now[-1].index(max(data_now[-1]))]
                print(f'取{now_name}')
                node_now = Node(now_name, parent=new_child) 
                self.tree.append(node_now)
                self.info += '  '*recursion_num + f'  按照多数投票原则，此时可以取 {head_now[now_DTR_id]}={now_name}，停止分割\n'  
                continue
            if len(data_now[-1]) == 1:
                node_now = Node(data_now[now_DTR_id][0], parent=new_child) 
                self.tree.append(node_now) 
                self.info += '  '*recursion_num + f'  此时{head_now[now_DTR_id]}只有一个取值，故取 {head_now[now_DTR_id]}={data_now[now_DTR_id][0]}，停止分割\n'  
                print('搜索到头了')
                continue
            # elif 
            else:
                smallq2_1 = SmallQ2(data_now, head_now)
                smallq2_1.get_max_G(DTR_id=now_DTR_id, head_str='  '*(recursion_num+1))
                for i_sm_g, sm_e in enumerate(smallq2_1.E_all):
                    print(smallq2_1.heads[smallq2_1.G_all_ids[i_sm_g]], sm_e)
                    # print('---------------------------------------------------')
                    # print(smallq2_1.info)
                    # print('---------------------------------------------------')
                
                self.info += smallq2_1.info + '\n'
                # 计算得到最大的列
                max_e_id = smallq2_1.G_all_ids[smallq2_1.G_all.index(max(smallq2_1.G_all))]
                name_now = smallq2_1.heads[smallq2_1.G_all_ids[i_sm_g]]
                print(f'选择{max_e_id}, {name_now}')
                print('---------------------------------------------------')
                # node_now1 = Node(name_now, parent=new_child) 
                # self.tree.append(node_now1) 
                # self.solveQ2_2(data_now, head_now, DTR_id=now_DTR_id, parent=node_now1, recursion_num=recursion_num+1)
                self.solveQ2_2(data_now, head_now, DTR_id=now_DTR_id, parent=new_child, recursion_num=recursion_num+1)


        return self.info


    def solveQ2(self, DTR_id=2):
        self.tree = []
        try:
            del self.root_node
        except:
            pass
        # self.__init__()
        print('DTR_id', DTR_id)

        self.solveQ2_1(DTR_id)
        self.solveQ2_2(self.data, self.heads, DTR_id)

        self.info += '\n综上所述，生成的判定树如下：\n'
        for pre, fill, node in RenderTree(self.tree[0]):
            print(f"{pre}{node.name}")
            self.info += f"{pre}{node.name}\n"

        return self.info
            
class SmallQ2():
    def __init__(self, data, heads):
        self.data = data
        self.heads = heads
        self.data_num = sum(data[-1])  # 数据总量
        # print('data_num', self.data_num)
        self.info = ''
        # 选中表头的项提取出其对应的表格
    def seperate_keys(self, head, value, data, heads):
        head_id = heads.index(head)
        rows_selected = [i for i, v in enumerate(data[head_id]) if v == value]
        head_selected = [h for h in heads if h != head]
        data_selected = []
        for i in range(len(data)):
            if i == head_id:
                continue
            data_selected.append([data[i][j] for j in range(len(data[0])) if j in rows_selected])

        # print(head_selected, data_selected)

        # 合并相同行
        labels = np.array(data_selected[:-1]).T
        count = data_selected[-1]

        return comb_same_lines(labels, count)

    def get_max_G(self, DTR_id=0, head_str=''):# 判定树根节点对应列数
        self.info = ''
        # print(self.data[DTR_id])
        last_labels_ar = np.array([self.data[DTR_id]]).T
        last_counts_ar = np.array([self.data[-1]]).T
        self.info += head_str + '计算整体信息量：\n'
        last_labels_ar, last_counts_ar = comb_same_lines(last_labels_ar, last_counts_ar)
        last_freq = np.array(last_counts_ar) / self.data_num
        last_freq = np.round(last_freq, 4)
        total_ar = np.array([['Total', self.data_num, 1.0]]).T
        # now_exel = np.vstack((np.hstack((np.array([['Count', 'Frequency']]).T, last_labels_ar, last_counts_ar, last_freq)), total_ar))
        now_exel = np.hstack((np.array([['', 'Count', 'Frequency']]).T, np.hstack((last_labels_ar, last_counts_ar, last_freq)).T, total_ar))
        self.info += '\n' + get_2dlist_print(now_exel, head=head_str+head_str) + '\n'
        # 计算整体信息增益
        # I_all = -np.sum(np.log2(last_freq) * last_freq)
        I_all_total = [- np.log2(last_freq[i]) * last_freq[i] if last_freq[i] else 0 for i in range(last_freq.shape[0])]
        I_all_total = sum(I_all_total)[0]
        count_str = [str(lca[0]) for lca in  last_counts_ar]
        Ixs = ','.join(count_str)
        # print(np.array(last_counts_ar).T.tolist()[0])
        self.info += head_str + f'I({Ixs}) = -Σpi*log_2(pi) = {round(I_all_total, 4)}\n'

        # 计算各个信息增益
        G_all = []
        E_all = []
        G_all_ids = []
        DTR_types = list(set(self.data[DTR_id]))
        for i in range(len(self.heads) - 1):
            if i == DTR_id:
                continue
            now_types = list(set(self.data[i]))
            

            data_mat_now = np.zeros((len(DTR_types), len(now_types)))
            for jms in range(len(self.data[0])):
                now_label = self.data[i][jms]
                data_mat_now[DTR_types.index(self.data[DTR_id][jms]), now_types.index(now_label)] += self.data[-1][jms]

            data_mat_now = data_mat_now.T.astype('int')
            # now_show_mat = 
            # print(self.heads[i])
            # print(np.array([[self.heads[i]]+now_types+['Total']]).T)
            # print(np.array([DTR_types+['Total']]))
            # print(data_mat_now)
            # print(np.append(np.sum(data_mat_now, axis=0), self.data_num).reshape(1,-1), np.sum(data_mat_now, axis=1).reshape(-1,1))
            

            res_mat_now =  np.hstack((
                        np.array([[self.heads[i]]+now_types+['Total']]).T,
                        np.vstack((np.array([DTR_types+['Total']]),
                        np.hstack((data_mat_now, np.sum(data_mat_now, axis=1).reshape(-1,1))),
                        np.append(np.sum(data_mat_now, axis=0), int(self.data_num)).reshape(1,-1)))
            ))
            
            self.info += f'\n{head_str}计算{self.heads[i]}属性信息增益：\n'
            self.info += '\n' + get_2dlist_print(res_mat_now, head='  ' + head_str) + '\n'
            I_now_all = []
            for i_id_og in data_mat_now:
                i_id = i_id_og / np.sum(i_id_og)
                I_all = sum([- np.log2(i_id[i]) * i_id[i] if i_id[i] else 0 for i in range(i_id.shape[0])])
                I_now_all.append(I_all)

            E_now = np.sum(np.sum(data_mat_now, axis=1) / self.data_num * np.array(I_now_all))
            # print(E_now)
            E_all.append(E_now)
            E_print_str_lst = []
            for iee in range(len(I_now_all)):
                I_xs = ','.join(data_mat_now[iee].astype('int').astype('str').tolist())
                E_print_str_lst.append(f'{int(float(res_mat_now[iee+1][-1]))}/{self.data_num}*I({I_xs})')

            E_result_lst = []
            for iee in range(len(I_now_all)):
                E_result_lst.append(f'{round(float(res_mat_now[iee+1][-1])/self.data_num, 4)}*{round(I_now_all[iee], 4)}')
            # print('+'.join(E_print_str_lst))
            self.info += head_str + f'E({self.heads[i]}) = '+'+'.join(E_print_str_lst)+'\n'+head_str+' = '+'+'.join(E_result_lst)+'\n'+head_str+' = '+str(round(E_now, 4))+'\n'

            gain_now = I_all_total - E_now
            self.info += head_str + f'Gain({self.heads[i]}) = I({Ixs})-E({self.heads[i]}) = '+str(round(gain_now, 4))
            G_all.append(gain_now)
            G_all_ids.append(i)
            # break

        self.G_all = G_all
        self.E_all = E_all
        self.G_all_ids = G_all_ids
        # print(G_all, G_all_ids)

    

if __name__ == '__main__':

    ARS = AssociationRulesSolve(cols=6,        # 表格列数 
                 data_path='./data/1_5.csv',  
                )  
    
    q1_res = ARS.solveQ1(s_th=0.2,     # 最小支持度阈值
                        c_th=0.75,      # 最小置信度阈值
                        SAR_id=2,      # 要求的强关联规则输出的列对应id
                        SAR_deg=3,     # 解频繁n项集 
                        )
    print(q1_res)
    q2_res = ARS.solveQ2(DTR_id=2)
    q2_res = ARS.solveQ2(DTR_id=3)
    # print(q2_res)
