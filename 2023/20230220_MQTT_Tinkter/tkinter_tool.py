def set_center(window, width, height):
    # window.update()
    # ���ھ��У���ȡ��Ļ�ߴ��Լ��㲼�ֲ�����ʹ���ھ���Ļ����
    screenwidth = window.winfo_screenwidth()
    screenheight = window.winfo_screenheight()
    size_geo = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    window.geometry(size_geo)
