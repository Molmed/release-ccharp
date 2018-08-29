import pyperclip


def copy_to_clipboard(var):
    if isinstance(var, set):
        var = list(var)
    if isinstance(var, list):
        var = '\n\n'.join(var)
    print('copied to clipboard:\n{}'.format(var))
    pyperclip.copy('{}'.format(var))
