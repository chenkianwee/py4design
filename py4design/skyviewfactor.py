'''
PART 1 - DISCRETIZATION OF 4-PI SPACE
@author: Tiangang Yin
Reference: Yin, T., Gastellu-Etchegorry, J.P., Lauret, N., Grau, E. and Rubio, J., 2013. A new approach of direction discretization and oversampling for 3D anisotropic radiative transfer modeling. Remote Sensing of Environment, 135, pp.213-223.
'''
import math
import py3dmodel

pi2 = math.pi*2

def wrapTo2PI(stradiance):
    result = 0.0
    if stradiance == pi2:
        return pi2;
    else:
        result = math.fmod(stradiance, pi2);
        if result < 0:
            return (result + pi2);
    return result

class direction(object):
    def __init__(self, x1=0.0, y1=0.0, z1=0.0):
        self.x=x1;
        self.y=y1;
        self.z=z1;
        
    def printNorm(self):
        print math.sqrt(math.pow(self.x,2)+math.pow(self.y,2)+math.pow(self.z,2))
        
    def reverseDir(self):
        return direction(-self.x,-self.y,-self.z);
        

def thetaPhiToVectorDir(theta, phi):
    epsilon = 1E-10;
    thetaInRad = theta;
    phiInRad = phi;
    cosTheta = math.cos(thetaInRad);
    cosPhi = math.cos(phiInRad);
    sinTheta = math.sin(thetaInRad);
    sinPhi = math.sin(phiInRad);
    
    dir = direction(sinTheta * cosPhi, sinTheta * sinPhi, cosTheta)
    return dir



class tgDirs(object):
    '''
    classdocs
    '''


    def __init__(self, nbDirs=2000):
        '''
        Constructor
        '''
        self.nbDirs = nbDirs;
        
        if self.nbDirs ==2:
            self.num_updirect = self.nbDirs / 2;
            self.num_layer = 1;
        else:
            if self.nbDirs % 2 == 1:
                self.nbDirs += 1;
            self.num_updirect = self.nbDirs / 2;
            self.num_layer = int(math.ceil((math.sqrt(pi2 * float(self.num_updirect))) / 4));
        
        self.__listDir=[];
        
        self.generateDirs();
        
    def generateDirs(self):

        delta_theta = math.pi / 2 / (float(self.num_layer));

        shift_const=[0]*self.num_layer;
        numSAcnt = 0;
        iter = 0; 
        
        
        while not iter == 2:
            omega_rem = pi2;
            theta_rem = math.pi / 2;
            num_layer_rem = self.num_layer;
            num_direct_rem = self.num_updirect;
            omega_unit = omega_rem / num_direct_rem;
            numSA_lastlayer = 1;
            
            theta_begin_layer = 0
            theta_end_layer = 0
            
            for i in range(self.num_layer):
                if i == 0:
                    theta_begin_layer = 0.0;
                    phi_begin_layer = 0.0;
                else:
                    theta_begin_layer = theta_end_layer;
                expect_delta_theta = theta_rem / num_layer_rem;
                expect_solid_angle = pi2 * (math.cos(theta_begin_layer) - math.cos(theta_begin_layer + expect_delta_theta));
                numSA_layer = int(round(expect_solid_angle / omega_unit)); 
                if numSA_layer < 2:
                    numSA_layer = 2
                    theta_end_layer = theta_begin_layer + expect_delta_theta;
                    omega_layer = (math.cos(theta_begin_layer) - math.cos(theta_end_layer)) * pi2;
                else:
                    omega_layer = omega_unit * numSA_layer;
                    theta_end_layer = math.acos(math.cos(theta_begin_layer) - omega_layer / pi2);
                    
                if iter == 0:
                    if numSA_layer == numSA_lastlayer:
                        numSAcnt += 1
                        for k in range(i - numSAcnt, i):
                            shift_const[k] = numSAcnt;
                    else:
                        numSAcnt = 0;
                        shift_const[i] = numSAcnt;
                    
                delta_theta = theta_end_layer - theta_begin_layer
                theta_centroid = math.acos((math.cos(theta_begin_layer)+math.cos(theta_end_layer))/2)
                if iter==1:
                    if shift_const[i] == 0 or shift_const[i] == 1:
                        phi_begin_layer = phi_begin_layer + 1 / numSA_lastlayer * math.pi;
                    else:
                        phi_begin_layer = phi_begin_layer + 1 / numSA_lastlayer * math.pi * (1 + 1 / float((shift_const[i])))
                    delta_phi = pi2 / numSA_layer;               
                    for j in range(numSA_layer):
                        phi_centroid = wrapTo2PI(phi_begin_layer + (j+0.5) * delta_phi);
                        dir = thetaPhiToVectorDir(theta_centroid, phi_centroid);
                        self.__listDir.append(dir);
#                         print dir.x, dir.y, dir.z
                num_layer_rem = num_layer_rem - 1;
                omega_rem = omega_rem - omega_layer;
                theta_rem = theta_rem - delta_theta;
#                 print num_direct_rem
                num_direct_rem = num_direct_rem - numSA_layer;
                if not num_direct_rem == 0:
                    omega_unit = omega_rem / num_direct_rem;
                numSA_lastlayer = numSA_layer;
            iter+=1;
            
        for i in reversed(range(self.num_updirect)):
            self.__listDir.append(self.__listDir[i].reverseDir())
        
    def printDirList(self, mode=0):
        if mode==0:
            for dir in self.__listDir:
                print dir.x, dir.y, dir.z
    #             dir.printNorm()
        elif mode==1:
            for dir in self.getDirUpperHemisphere():
                print dir.x, dir.y, dir.z
        elif mode==2:
            for dir in self.getDirLowerHemisphere():
                print dir.x, dir.y, dir.z
        
    def getDirList(self):
        return self.__listDir
    
    def getDirUpperHemisphere(self):
        return self.__listDir[0:self.num_updirect]
    
    def getDirLowerHemisphere(self):
        return self.__listDir[self.num_updirect:self.nbDirs]
    
    def getNbDir(self):
        return self.nbDirs
#        
#if __name__ == '__main__':
#    parser = argparse.ArgumentParser(prog='fourpispace.py', description='Using Iterative Square Uniform Discretization (IUSD) approach to generate sphere/hemisphere sampling of equal solid angles')
#    parser.add_argument('nbDirs', type=int, help='Number of predefined directions')
##     parser.add_argument('-minw', '--minWavelength', type=float, help='Define the minimum wavelength range in um (default: 0.1)')  
#          
#    args = parser.parse_args()
#    if args.nbDirs:
#        obj = tgDirs(args.nbDirs);
##         obj.__listDir
#        obj.printDirList(2)
##    

#%%%%%%%%%%%%%%%
""" PART 2: Sky View Factor Calculation
    @author: Tiffany Sin  """

Ndir = 500
unitball = tgDirs(Ndir)

def calc_SVF(coord, compound):

    visible=0.; blocked = 0.;
    for direction in unitball.getDirUpperHemisphere():
        (X,Y,Z) = (direction.x,direction.y,direction.z)
        occ_interpt, occ_interface = py3dmodel.calculate.intersect_shape_with_ptdir(compound,coord,(X,Y,Z))
        if occ_interpt != None: blocked +=1.0
        else: visible +=1.0
    svf = (visible)/(visible+blocked);
    return svf
