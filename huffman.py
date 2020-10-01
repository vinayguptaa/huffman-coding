import heapq
import os

# trying to create a tree so as to generate huffman code
class BinaryTreeNode:
# each tree node has a value,a frequency,a left node and a right node
    def __init__(self,value,freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None
        
    #########
    #so that constructing the min heap knows how to compare such nodes (operator overloading)
    
    def __lt__(self,other):
        return self.freq < other.freq
    
    def __eq__(self,other):
        return self.freq == other.freq
    
    #########

class HuffmanCoding:
    def __init__(self,path):
        self.path = path
        self.__heap = []
        self.__codes = {}
        self.__reverseCodes = {}
      
    def __make_frequency_dict(self,text):
        d = {}
        for ch in text:
            d[ch] = d.get(ch,0) + 1 
        return d
    
    def __buildHeap(self,freq_dict):
        for key in freq_dict:
            freq = freq_dict[key]
            btn = BinaryTreeNode(key,freq)
            heapq.heappush(self.__heap, btn)
    
    def __buildTree(self):
        #last left in the heap will be our root
        while (len(self.__heap) > 1):
            btn1 = heapq.heappop(self.__heap)
            btn2 = heapq.heappop(self.__heap)
            freq_sum = btn1.freq + btn2.freq
            newNode = BinaryTreeNode(None,freq_sum)
            newNode.left = btn1
            newNode.right = btn2
            heapq.heappush(self.__heap, newNode)
    
    def __buildCodesHelper(self,root,curr_bits):
        if root is None:
            return
        
        if root.value is not None:
            self.__codes[root.value] = curr_bits
            #####
            #this will help in decompressing part
            self.__reverseCodes[curr_bits] = root.value
            #####
            return
        
        self.__buildCodesHelper(root.left,curr_bits+"0")
        self.__buildCodesHelper(root.right,curr_bits+"1")
    
    def __buildCodes(self):
        root = heapq.heappop(self.__heap)
        self.__buildCodesHelper(root,"")
    
    def __getEncodedText(self,text):
        encoded_text = ""
        for ch in text:
            encoded_text += self.__codes[ch]
        return encoded_text
    
    def __getPaddedEncodedText(self,encoded_text):
        padded_amount = 8 - (len(encoded_text)%8)
        
        for i in range(padded_amount):
            encoded_text += "0"
            
        padding_info = "{0:08b}".format(padded_amount)
        padded_encoded_text = padding_info + encoded_text
        
        return padded_encoded_text
    
    def __getBytesArray(self,padded_encoded_text):
        bytes_array = []
        for i in range(0,len(padded_encoded_text),8):
            byte = padded_encoded_text[i:i+8]
            bytes_array.append(int(byte,2))
            
        return bytes_array
    
    def compress(self):
        #get file from the path
        #get text from the file
        file_name, file_extension = os.path.splitext(self.path)
        output_path = file_name + '.bin'
        
        with open(self.path, 'r+') as file , open(output_path,'wb') as output:
            text = file.read() #reading the file
            text = text.rstrip() #remove trailing spaces

            #make freq dict from the text
            freq_dict = self.__make_frequency_dict(text)

            #construct min heap from freq dict
            self.__buildHeap(freq_dict)

            #construct the binary tree
            self.__buildTree()

            #build the codes from binary tree
            self.__buildCodes()

            #create encoded text using codes
            encoded_text = self.__getEncodedText(text)

            #pad the encoded text
            #### we want to make it all th set of 8, so we will add zeroes at last, to keep track of how many zeroes we
            #### added we will enter that binary number in 8 bits at the start only like if we added 3 zeroes at the last
            #### then we will add 00000011 at starting
            padded_encoded_text = self.__getPaddedEncodedText(encoded_text)


            bytes_array = self.__getBytesArray(padded_encoded_text)
            #put the encoded text in binaryfile
            final_bytes = bytes(bytes_array)

            #return the file as output
            output.write(final_bytes) #writing in file
        print("COMPRESSED")
        return output_path
    
    def __removePadding(self,text):
        padding_info = text[:8]
        extra_padding = int(padding_info, 2) #base 2
        text = text[8:]
        
        #final_text = after removing the zeroes we added initially
        final_text = text[:-1*extra_padding]
        return final_text
    
    def __decodeText(self,text):
        decoded_text = ""
        curr_bits = ""
        
        for bit in text:
            curr_bits += bit
            if curr_bits in self.__reverseCodes:
                decoded_text += self.__reverseCodes[curr_bits]
                curr_bits = ""
                
        return decoded_text
    
    def decompress(self, input_path):
        file_name, file_extension = os.path.splitext(input_path) 
        output_path = file_name + '_decompressed' + '.txt'
        
        with open(input_path, 'rb') as file , open(output_path, 'w') as output:
            #reading one at a time
            byte = file.read(1)
            bit_string = ""
            
            while byte:
                #byte in int format
                byte =  ord(byte)
                bits = bin(byte)[2:].rjust(8,'0')
                bit_string += bits
                byte = file.read(1)
            actual_text = self.__removePadding(bit_string)
            decoded_text = self.__decodeText(actual_text)
            output.write(decoded_text)
        print("DECOMPRESSED")
            

path = "/Users/vinaygupta/Desktop/sample.txt" #jusr an example ## copy paste your text file path here
h = HuffmanCoding(path)
output_path = h.compress()
h.decompress(output_path)

# .bin extension for output file is the biary file indication and to see the result see the memory the sample.txt
# is taking and the sample.bin (output) is taking, it is almost almost half (see from get info and then bytes taken)
