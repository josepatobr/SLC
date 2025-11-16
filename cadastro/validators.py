def is_valid_cpf(cpf):
    cpf = "".join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)

    resto = soma % 11
    dv1_calculado = 0 if resto < 2 else 11 - resto

    if dv1_calculado != int(cpf[9]):
        return False

    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)

    resto = soma % 11
    dv2_calculado = 0 if resto < 2 else 11 - resto

    if dv2_calculado != int(cpf[10]):
        return False

    return True
