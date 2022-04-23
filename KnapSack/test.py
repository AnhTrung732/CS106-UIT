import os
class Test:
    def __init__(self, test_to_load):
        self.number = 0
        self.capacities = []
        self.values = []
        self.weights  = []
        self.file = ''
        self.load(test_to_load)

    def load(self, test):
        type_test, num_test, range_test, sample_test = test.split("-")
        #print(type_test, num_test, range_test, sample_test)
        type_test = str(0)*(2-len(type_test)) + type_test
        num_test = str(0)*(5-len(num_test)) + num_test
        sample_test = str(0)*(3-len(sample_test)) + sample_test
        type_name = [fname for fname in os.listdir('kplib') if type_test in fname] 
        #print(type_name)
        type_dir = 'kplib' + '/' + type_name[0]
        num_name = [fname for fname in os.listdir(type_dir) if num_test in fname] 
        #print(num_name)
        range_dir = 'kplib' + '/' + type_name[0] + '/' + num_name[0]
        range_name = [fname for fname in os.listdir(range_dir) if range_test == fname[1]] 
        #print(range_name)
        sample_dir = 'kplib' + '/' + type_name[0] + '/' + num_name[0] + '/' + range_name[0]
        sample_name = [fname for fname in os.listdir(sample_dir) if sample_test in fname] 
        #print(sample_name)
        file =  'kplib' + '/' + type_name[0] +'/' + num_name[0] + '/' + range_name[0] + '/' + sample_name[0]
        #print(file)
        self.file = file

    def process(self):
        file = self.file
        weight = []
        with open(file) as test_file:
            rows = test_file.read().split('\n')
        #print(rows)
        self.number = int(rows[1])
        self.capacities.append(int(rows[2]))
        for row in rows:
            try:
                row_1, row_2 = row.split(" ")
                self.values.append(int(row_1))
                weight.append(int(row_2))
            except Exception:
                pass
        self.weights.append(weight)
        #print(self.number, self.capacities, self.values, self.weights)
        return (self.number, self.capacities, self.values, self.weights)




if __name__ == '__main__':
    test = Test("1-50-0-5")
    test.process()