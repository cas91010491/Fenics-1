# _*_ coding:utf-8 _*_
"""
This demo program solves Maxwell equation in 2D
    curl curl u - grad div u - omega^2 u = f    in  \Omega
    u x n = 0   on \Omega

on the unit square with  f given by
    omega = 1
    f = curl curl u - u - grad div u = (f1, f2)
    f1 = -2*x[1]*(x[1] + 1)*exp(x[1])
    f2 = ((pi**2-2)*sin(pi*x[0]) - 2*pi*cos(pi*x[0]))*exp(x[0])
and exact solution given by
    u1 = x[1]*(x[1] - 1)*exp(x[1])
    u2 = sin(pi*x[0])*exp(x[0])
"""

from dolfin import *
import numpy,sys
import numpy as np
from math import *  #import pi
import scitools.BoxField
import scitools.easyviz as ev

# Create mesh and define function space
# For example: python Maxwell_S2D.py  8 8 2 
nx = int(sys.argv[1])
ny = int(sys.argv[2])
nz = int(sys.argv[3])
mesh= UnitSquare( nx, ny)
U_h = VectorFunctionSpace(mesh, "Lagrange", nz) #nz次元

# Define trial and test function
u = TrialFunction(U_h)
v = TestFunction(U_h)
 

# Define boundary condition(x = 0 or x = 1 or y=0 or y=1) u x n = u_1*n_2 - u_2*n1 = 0
def boundary1(x):
    return x[0] > 1.0 - DOLFIN_EPS
def boundary2(x):
    return x[1] > 1.0 - DOLFIN_EPS
def boundary3(x):
    return x[0] < DOLFIN_EPS
def boundary4(x):
    return x[1] < DOLFIN_EPS
u0 = Constant("0.0")
bc1 = DirichletBC(U_h.sub(1), u0, boundary1)
bc2 = DirichletBC(U_h.sub(0), u0, boundary2)
bc3 = DirichletBC(U_h.sub(1), u0, boundary3)
bc4 = DirichletBC(U_h.sub(0), u0, boundary4)
bc=[bc1,bc2,bc3,bc4]
print("bc is created!")
	
# Define parameter and f
omega = Constant('1.0')
class f_expression(Expression):
    def eval(self, value, x):
        value[0] = -2*x[1]*(x[1] + 1)*exp(x[1])
        value[1] = ((pi**2-2)*sin(pi*x[0]) - 2*pi*cos(pi*x[0]))*exp(x[0])
    def value_shape(self):
        return (2,)
f = f_expression()
Ue=VectorFunctionSpace(mesh,"Lagrange",degree=5)
ff = interpolate(f,Ue)

# Define a higher-order approximation to the exact solution
Ue=VectorFunctionSpace(mesh,"Lagrange",degree=3)
class MyExpression1(Expression):
    def eval(self, value, x):
        value[0] = x[1]*(x[1] - 1)*exp(x[1])
        value[1] = sin(pi*x[0])*exp(x[0])
    def value_shape(self):
        return (2,)
u_exact = MyExpression1()
u_ex = interpolate(u_exact,Ue)

# Define variational form
n = FacetNormal(mesh) 
a = inner(curl(u),curl(v))*dx + inner(div(u),div(v))*dx - omega**2*inner(u,v)*dx
L = inner(ff,v)*dx

# Solve
(A,b) = assemble_system(a,L,bc)
print("A and b is assembled!")
u0 = Function(U_h)
solver = KrylovSolver("cg", "ilu")
solver.parameters["absolute_tolerance"] = 1E-20	
solver.parameters["relative_tolerance"] = 1E-20
solver.parameters["maximum_iterations"] = 3000
set_log_level(DEBUG)
solve(A, u0.vector(), b)
	
# Save solution in VTK format
file = File("Data/Maxwell S2D_%gx%gP%g.pvd"%(nx,ny,nz))
file << u0

# Plot approximation solution 
visual_mesh = plot(mesh,title = "Mesh")
visual_u = plot(u0,wireframe =  True,title = "the approximation of u",rescale = True , axes = True, basename = "deflection" ,legend ="u0")
visual_u1 = plot(u0[0],title="the approximation of u1",rescale = True , axes = True, basename = "deflection" ,legend ="u1")
visual_u2 = plot(u0[1],wireframe =  True,title = "the approximation of u2",rescale = True , axes = True, basename = "deflection" ,legend ="u2")
visual_mesh.write_png("Image/P%g_mesh_%gx%g.png"%(nz,nx,ny))
visual_u.write_png("Image/P%g_u_%gx%g"%(nz,nx,ny))
visual_u1.elevate(-65) #tilt camera -65 degree(latitude dir)
visual_u2.elevate(-65)
visual_u1.write_png("Image/P%g_u1_%gx%g.png"%(nz,nx,ny))
visual_u2.write_png("Image/P%g_u2_%gx%g.png"%(nz,nx,ny))

# Plot exact solution 
visual_ue1 = plot(u_ex[0],title="the exact solution of u1",rescale = True , axes = True, basename = "deflection" ,legend ="u1")
visual_ue2 = plot(u_ex[1],wireframe = True,title="the exact solution of u2",rescale = True , axes = True, basename = "deflection" ,legend ="u2")
visual_ue1.elevate(-65) #tilt camera -65 degree(latitude dir)
visual_ue2.elevate(-65) #tilt camera -65 degree(latitude dir)
visual_ue1.write_png("Image/P%gu1_exact_%gx%g.png"%(nz,nx,ny))
visual_ue2.write_png("Image/P%gu2_exact_%gx%g.png"%(nz,nx,ny))
#interactive()

"""
# Plot with scitools
X = 0; Y = 1;
u1,u2 = u0.split(deepcopy = True)

us = u1 if u1.ufl_element().degree() == 1 else \
     interpolate(u1, FunctionSpace(mesh, 'Lagrange', 1))
u_box = scitools.BoxField.dolfin_function2BoxField(us, mesh, (nx,ny), uniform_mesh=True)


ev.contour(u_box.grid.coorv[X], u_box.grid.coorv[Y], u_box.values, 20, 
           savefig='Image/Contour of u1_P%g(mesh:%g-%g).png'% (nz,nx,ny), title='Contour plot of u1', colorbar='on')

ev.figure()
ev.surf(u_box.grid.coorv[X], u_box.grid.coorv[Y], u_box.values, shading='interp', colorbar='on', title='surf plot of u1', savefig='Image/Surf of u1_P%g(mesh:%g-%g).png'% (nz,nx,ny))

#ev.figure()
#ev.mesh(u_box.grid.coorv[X], u_box.grid.coorv[Y], u_box.values,colorbar='on',shading='interp', title='mesh plot of u1', savefig='Image/Mesh of u1_P%g(mesh:%g-%g).png'% (nz,nx,ny))

# Plot exact solution
u1_ex,u2_ex = u_ex.split(deepcopy = True)

u1_ex = u1_ex if u1_ex.ufl_element().degree() == 1 else \
     interpolate(u1_ex, FunctionSpace(mesh, 'Lagrange', 1))
u_box = scitools.BoxField.dolfin_function2BoxField(u1_ex, mesh, (nx,ny), uniform_mesh=True)

ev.figure()
ev.contour(u_box.grid.coorv[X], u_box.grid.coorv[Y], u_box.values, 20, 
           savefig='Image/Contour of exact solution u1_P%g(mesh:%g-%g).png'% (nz,nx,ny), title='Contour plot of exact u1',colorbar='on')

ev.figure()
ev.surf(u_box.grid.coorv[X], u_box.grid.coorv[Y], u_box.values, shading='interp', colorbar='on', title='surf plot of exact u1', savefig='Image/Surf of exact solution u1_P%g(mesh:%g-%g).png'% (nz,nx,ny))

#ev.figure()
#ev.mesh(u_box.grid.coorv[X], u_box.grid.coorv[Y], u_box.values, colorbar="on", title='mesh plot of exact u1', savefig='Image/Mesh of exact solution u1_P%g(mesh:%g-%g).png'% (nz,nx,ny))
"""

#Define L2 norm and H1 norm relative errors 
u1_error = (u0[0]-u_ex[0])**2*dx
u2_error = (u0[1]-u_ex[1])**2*dx
u1_ex_L2 = u_ex[0]**2*dx
u2_ex_L2 = u_ex[1]**2*dx

L2_error_u1 = sqrt(assemble(u1_error)/assemble(u1_ex_L2))
L2_error_u2 = sqrt(assemble(u2_error)/assemble(u2_ex_L2))

Curl_Div_error_u1 = sqrt(assemble(inner(curl(u0[0]-u_ex[0]),curl(u0[0]-u_ex[0]))*dx + inner(div(u0[0]-u_ex[0]),div(u0[0]-u_ex[0]))*dx)/assemble(inner(curl(u_ex[0]),curl(u_ex[0]))*dx + inner(div(u_ex[0]),div(u_ex[0]))*dx))
Curl_Div_error_u2 = sqrt(assemble(inner(curl(u0[1]-u_ex[1]),curl(u0[1]-u_ex[1]))*dx + inner(div(u0[1]-u_ex[1]),div(u0[1]-u_ex[1]))*dx)/assemble(inner(curl(u_ex[1]),curl(u_ex[1]))*dx + inner(div(u_ex[0]),div(u_ex[0]))*dx))


print("h=" ,CellSize(mesh))
print("The number of cells(triangle) in the mesh:" ,mesh.num_cells())
print("The number of vertices in the mesh:" ,mesh.num_vertices())
print("L2_error_u1=" ,L2_error_u1)
print("L2_error_u2=" ,L2_error_u2)
print("Curl_error_u1=" ,Curl_Div_error_u1)
print("Curl_error_u2=" ,Curl_Div_error_u2)


file_object = open('Error_P%g.txt'%(nz),'a')
file_object.writelines("The number of cells(triangle) in the mesh:%g" %(mesh.num_cells()))
file_object.writelines("The number of vertices in the mesh:%g"%(mesh.num_vertices()))
file_object.writelines("Mesh:%gx%gP%g\n"%(nx,ny,nz))
file_object.writelines("L2_error_u1= %g\n"%(L2_error_u1))
file_object.writelines("L2_error_u2= %g\n"%(L2_error_u2))
file_object.writelines("Curl_error_u1= %g\n" %(Curl_Div_error_u1))
file_object.writelines("Curl_error_u2= %g\n\n"%(Curl_Div_error_u2))
file_object.close()

file_output = open('Ratio_P%g.txt'%(nz),'a')
E = np.array([nx,L2_error_u1,L2_error_u2,Curl_Div_error_u1,Curl_Div_error_u2])
print(E)
file_output.writelines("%g %g %g %g %g\n"%(E[0],E[1],E[2],E[3],E[4]))


