from setuptools import setup, find_packages

setup(
    name='grok-cli',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click',
        'composio_core',
        'composio_langchain',
        'langchain',
        'langchain_openai',
        'langchain_community',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'grok-cli = grok_cli.cli:main',
        ],
    },
    author='Your Name',
    description='A CLI tool for interacting with xAI Grok 4',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown',
)