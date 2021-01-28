import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='UCDRFLabUtilities',
    version='0.0.1',
    author='Mark Travers',
    author_email='mark.2.travers@ucdenver.edu',
    description='Commonly used utilities in the UC Denver RF lab.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/MarkTravers/UCDRFLabUtilities',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)