# Tmp notes

## Linie z wartościami, które mogą ulegać zmianie (szerokość kolumn, wymiary okna itp.)
**main_window.py**
```python
    self.table.setColumnWidth(3, 565)
    
    window.resize(900, 400)
```

**efibootmgr.py**
```python
    cmd = ['pkexec', '/usr/sbin/efibootmgr']
```