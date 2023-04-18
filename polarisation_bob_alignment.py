from ukie_core.koheronOptimisation import PolarisationOptimiser

targetEr = float(input("Input the target extinction ratio in dB (decibel): "))
print(':::The target extinction ratio is:', targetEr, 'dB:::')

Base = PolarisationOptimiser(fineV=100,
                             zeroV=False,
                             minV=False,
                             randomV=False,
                             plot=True)

Base.run()
