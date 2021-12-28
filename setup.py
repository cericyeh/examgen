from distutils.core import setup

setup(name='Examgen',
      version='0.1',
      description='Exam generation tool',
      author='Eric Yeh',
      author_email='cericyeh@gmail.com',
      packages=[
          'examgen'
          ],
      install_requires=[
          'spacy'
          ]
)
