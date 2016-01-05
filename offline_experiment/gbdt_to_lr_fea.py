#! /bin/env python
# encoding=utf-8
# zouxianqi@domob.cn
#  1.gbdt模型每颗树的路径作为lr的每一维特征
#     需要先训练出gbdt模型
#	  叶子节点特征名是"leaf"
#
#

class GBDT_FEA_TREE():
	def __init__(self):
		self.fea_map =  {}
		self.l_branch = {}
		self.r_branch = {}
		self.leaf = 'leaf'	
		self.iter = -1

class FEA_FACTORY():
	def __init__(self):
		self._fea_map_file_path = './dump.raw.txt'
		self.forests = {}
		self.tree_num = 0
		self.leaf_map_fea = {}
		self.leaf_fea_index = 0

	def load_data(self):
		with open(self._fea_map_file_path,'r') as fin:
			tree_num = int(fin.readline().strip())
			fin.readline() # strip#
			tree = GBDT_FEA_TREE()
			for l in fin:
				if l.strip() == '#':
					tree.iter = self.tree_num
					self.forests[tree] = ""
					self.tree_num += 1
					tree = GBDT_FEA_TREE()
					continue

				l = l.strip().split('\t')	
				if l[0] == '-1':
					sys.stderr.write('feamap exceed.')
					sys.exit(-1)
				items = l[0].split(':')	

				tree.fea_map[items[0]] = items[1]
				if items[1] != tree.leaf:
					tree.l_branch[items[0]] = l[1]
					tree.r_branch[items[0]] = l[2]
				else:
					leaf_fea = str(self.tree_num)+','+items[0]
					if leaf_fea not in self.leaf_map_fea:
						self.leaf_fea_index += 1
						self.leaf_map_fea[leaf_fea] = self.leaf_fea_index

			tree.iter = self.tree_num
			self.forests[tree] = ""
			self.tree_num += 1

			if self.tree_num != tree_num:
				sys.stderr.write('tree num error')
				sys.exit(-1)

	def gen_fea(self, fpath, fea_out_path):
		with open(fpath, 'r') as fin, open(fea_out_path, 'w') as fout:
			for l in fin:
				l = l.strip().split(' ')
				fout.write("%s" % l[0])
				fea_list = [item.split(':')[0] for item in l[1:]]
				gbdt_fea_list = []
				for tree in fea_fact.forests:
					leaf_idx = self.path_tracking(fea_list, tree)
					leaf_fea = 	str(tree.iter)+','+leaf_idx
					gbdt_fea_idx = self.leaf_map_fea[leaf_fea]
					gbdt_fea_list.append(gbdt_fea_idx)
				gbdt_fea_list = sorted(gbdt_fea_list)
				for gbdt_fea_idx in gbdt_fea_list:
					fout.write(" %s:1" % gbdt_fea_idx)
				fout.write('\n')

	def path_tracking(self, fea_list, tree):
		fea = tree.fea_map['0']
		idx = '0'
		while fea != tree.leaf:
			idx = tree.l_branch[idx] if fea in fea_list else tree.r_branch[idx]
			fea = tree.fea_map[idx]
		return idx

	def dump_fea_map(self, fea_path):
		with open(fea_path, 'w') as fout:
			for k,v in self.leaf_map_fea.items():
				fout.write("%s\t%d\n" % (k,v))

	def load_fea_dump(self, fea_path):
		pass

if __name__ == '__main__':	
	fea_fact = FEA_FACTORY()
	fea_fact.load_data()
	fea_fact.dump_fea_map('gbdt_fea_map')
	fea_fact.gen_fea('./train_fea', './gbdt_fea_train') # new train feature for lr
	fea_fact.gen_fea('./test_fea', './gbdt_fea_test')   # new test feature  for lr
					
