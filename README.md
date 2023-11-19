# lab3
Программное средство для визуализации аналитики задач проекта Apache Kafka
## Для Windows:
### распаковка архива

tar -xvzf C:\путь_к_архиву\имя_архива.tar.gz -C C:\путь_к_папке\где_будет_распакован_архив    

(например: tar -xvzf C:\Users\Admin\Downloads\lab3-1.0.tar.gz -C C:\Users\Admin\Downloads\)    

Распакованный архив располагается в папке Downloads\lab3-1.0
### установка pip

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

python get-pip.py

### установка проекта 

cd Downloads\lab3-1.0

python setup.py install

Поскольку в файле setup.py прописаны зависимости проекта в виде install_requires (и также продублированы в архиве в папке lab3.egg-info/requires.txt, то эти зависимости подгружаются автоматически во время запуска setup.py

### запуск меню для построения графиков

cd lab3

python lab3_graphs.py

## Для Linux:
### распаковка архива

cd Downloads

tar -xf lab3-0.1.tar.gz

Распакованный архив располагается в папке Downloads\lab3-1.0

### установка pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

python3 get-pip.py

### установка проекта 

cd Downloads/lab3-1.0

python3 setup.py install

### запуск меню для построения графиков

cd lab3

python3 lab3_graphs.py
