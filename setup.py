import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='autopytic',  
     version='0.9',
     author="Robert Kruczek",
     author_email="kruczeknb1@gmail.com",
     description="A autopytic package",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/kruczekrobert/autopytic",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )