# 1• Write a Python program using a context manager (with) to open a text file in 
# read mode, read the entire content using read(), and print the number of 
# characters in the file.
# # A
# with open('f1.txt','r') as f:
#     print(len(f.read()))



# 2• Write a program that opens a file using a context manager, reads all lines 
# using readlines(), and prints only the lines that contain more than 10 
# characters.
# #A
# with open('f1.txt','r') as f:
#     print(list(filter(lambda x:len(x)>10,f.readlines())))



# 3• Write a program that creates a file and writes 3 lines using write(), reopens 
# the same file in append mode, appends 2 more lines, and finally reads and prints 
# the complete file content.
# # A
# with open("f2.txt",'w') as f:
#     f.write('line 1\n')
#     f.write('line 2\n')
#     f.write('line 3\n')
# with open("f2.txt",'a') as l:
#     l.write('line 4\n')
#     l.write('line 5')
# with open("f2.txt",'r') as k:
#     print(k.read())



# 4• Write a program that opens a file in read mode, reads the first 10 characters, 
# prints the current cursor position using tell(), moves the cursor back to the 
# beginning using seek(0), and reads the full content again.
# # A
# with open('f2.txt','r') as f:
#     print(f.read(10))
#     print(f.tell())
#     f.seek(0)
#     print(f.tell())



# 5• Create a custom context manager using a class that opens a file in write mode 
# in the __enter__ method, writes a line to the file, closes the file in the 
# __exit__ method, and properly prints or logs any exception information received 
# in __exit__.
# # A
# class cm:
#     def __init__(self,f,m):
#         self.f=f
#         self.m=m
#     def __enter__(self):
#         self.fo=open(self.f,self.m)
#         self.fo.write('lineee')
#         return self.fo
#     def __exit__(self, exc_type, exc, tb):
#         self.fo.close()
#         if exc_type:
#             print(exc_type, exc, tb)
#         return False
# with cm('f2.txt','w') as f:
#     pass
# f1=open('f2.txt','r')
# print(f1.read())


# f1=open('t.txt','w')
# f1.close()
# class A:
#     def __init__(self,f,m) -> None:
#         self.f=f
#         self.m=m
#     def __enter__(self):
#         print('enterded')
#         self.f1=open(self.f,self.m)
#         self.f1.write('l1')
#         return
#     def __exit__(self, exc_type, exc, tb):
#         self.f1.close()
#         print(exc_type)
#         print(tb)
#         print(exc)
#         return True
# with A('t.txt','w') as f:
#     print('in context')
#     raise Exception('Hello')



# 6• Create a custom context manager using @contextmanager from the contextlib 
# module that opens a file, yields the file object, and ensures the file is closed 
# even if an exception occurs.
# # A
# from contextlib import contextmanager
# @contextmanager
# def fun(file,m):
#     try:
#         f=open(file,m)
#         yield f
#     except Exception as e:
#         print("error ")
#         print(e)
#         yield None
#     else:
#         f.close()
#     finally:
#         print('closed')
# with fun('f.txt','r') as f:
#     if f is not None:
#         print(f.read())
#     else:
#         print('f is none')

# or


# from contextlib import contextmanager

# @contextmanager
# def fun(file, mode):
#     f = None
#     try:
#         f = open(file, mode)
#         f.write("A line\n")
#         yield f   # normal case
#     except Exception as e:
#         # This block runs if an exception is raised inside the with-block
#         print("Error caught inside context manager:")
#         print(f"Type: {type(e).__name__}, Message: {e}")
#         # Suppress the exception by not re-raising
#         # If you want it to propagate, just `raise` here instead
#     finally:
#         if f:
#             f.close()
#         print("File closed")
# with fun("f1.txt", "w") as f:
#     print("Inside with-block")
#     raise Exception("any")   # This will be caught inside fun

# 7• Write a program using a context manager that opens a file in read mode, uses a 
# loop to read the file in small chunks (for example, 5 characters at a time), 
# prints the cursor position after each read using tell(), uses seek() to move to 
# a specific position, and continues reading from there.
# # A
# class cm:
#     def __init__(self,f,m):
#         self.f=f
#         self.m=m
#     def __enter__(self):
#         self.fo=open(self.f,self.m)
#         return self.fo
#     def __exit__(self, exc_type, exc, tb):
#         self.fo.close()
# with cm('f2.txt','r') as f:
#     f.seek(0)
#     cs=5
#     while(True):
#         d=f.read(cs)
#         print(d)
#         if d=='':
#             break
#         print('file pointer at:',f.tell())