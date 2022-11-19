from Módulos_calculo import vigas

viga5 = vigas.posTensionedIsoBeam(0.2, 0.15, 0.14, 5)

# global variables

Pmin = viga5.Pmin()
equiLoad = viga5.equivalentLoad(Pmin)
Ap = viga5.Ap(Pmin)
instantLosses = viga5.instantLosses(Pmin, Ap)



# Algorithim

htrial = viga5.hflex()
print(f"h predim: {htrial}m")

