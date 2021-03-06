#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import math
import numpy as np
from dolfin import *
from scipy.sparse.linalg import LinearOperator
from scipy.sparse import csr_matrix
from numpy import intc
# krypy: https://github.com/andrenarchy/krypy
from krypy.krypy import linsys, utils
from pyamg import smoothed_aggregation_solver
#from solver_diagnostics import solver_diagnostics # pyamg
from matplotlib import pyplot as pp

parameters.linear_algebra_backend = "uBLAS"

def main():
    stokes_eoc2d()

def stokes_karman2d():
    # cf. Schäfer and Turek, Benchmark Computations of Laminar Flow Around a Cylinder, 1996
    # the mesh can be generated by
    #  $ gmsh -2 -clmax 0.025 msh_karman2d.geo
    #  $ dolfin-convert msh_karman2d.msh msh_karman2d.xml
    mesh = Mesh('msh_karman2d.xml')
    boundaries = MeshFunction('size_t', mesh, mesh.topology().dim()-1)
    boundaries.set_all(0)

    class Solid(SubDomain):
        def inside(self, x, on_boundary):
            return on_boundary and (x[1]<DOLFIN_EPS or x[1]>0.41-DOLFIN_EPS or 
                    (x[0]>DOLFIN_EPS and x[0]<2.2-DOLFIN_EPS))
    Solid().mark(boundaries, 1)

    class Inlet(SubDomain):
        def inside(self, x, on_boundary):
            return on_boundary and (x[0]<=DOLFIN_EPS)# or x[0]>=2.2-DOLFIN_EPS)
    Inlet().mark(boundaries, 2)

    dbcs = {
            1: Constant((0.0,0.0)),
            2: Expression(('4*x[1]*(0.41-x[1])/(0.41*0.41)','0.0'))
            }
    sol = solve_stokes(mesh, 
            u_init = Constant((0.0,0.0)),
            f = Constant((0.0,0.0)),
            boundaries = boundaries,
            dbcs = dbcs,
            scale_dt=0.01,
            u_file = File("results/velocity.pvd"),
            p_file = File("results/pressure.pvd"),
            )

def stokes_karman3d():
    # cf. Schäfer and Turek, Benchmark Computations of Laminar Flow Around a Cylinder, 1996
    # the mesh can be generated by
    #  $ gmsh -3 -clmax 0.04 msh_karman3d.geo
    #  $ dolfin-convert msh_karman3d.msh msh_karman3d.xml
    mesh = Mesh('msh_karman3d.xml')
    boundaries = MeshFunction('size_t', mesh, mesh.topology().dim()-1)
    boundaries.set_all(0)

    class Solid(SubDomain):
        def inside(self, x, on_boundary):
            return on_boundary and (x[1]<DOLFIN_EPS or x[1]>0.41-DOLFIN_EPS or 
                    x[2]<DOLFIN_EPS or x[2]>0.41-DOLFIN_EPS or
                    (x[0]>DOLFIN_EPS and x[0]<2.5-DOLFIN_EPS))
    Solid().mark(boundaries, 1)

    class Inlet(SubDomain):
        def inside(self, x, on_boundary):
            return on_boundary and (x[0]<=DOLFIN_EPS)# or x[0]>=2.2-DOLFIN_EPS)
    Inlet().mark(boundaries, 2)

    dbcs = {
            1: Constant((0.0,0.0,0.0)),
            2: Expression(('sin(pi*x[1]/0.41)*sin(pi*x[2]/0.41)','0.0','0.0'))
            }
    sol = solve_stokes(mesh, 
            u_init = Constant((0.0,0.0,0.0)),
            f = Constant((0.0,0.0,0.0)),
            boundaries = boundaries,
            dbcs = dbcs,
            scale_dt=0.01,
            u_file = File("results/velocity.pvd"),
            p_file = File("results/pressure.pvd"),
            )

def stokes_eoc2d(refines = 3):
    alpha = 20
    beta = 5

    sin0 = "sin(alpha*x[0]*t)"
    sin1 = "sin(alpha*x[1]*t)"
    cos0 = "cos(alpha*x[0]*t)"
    cos1 = "cos(alpha*x[1]*t)"
    u0 = sin0+"*"+sin1
    u1 = cos0+"*"+cos1

    d00_u0 = "(-alpha*alpha*t*t*t*"+u0+")"
    d11_u1 = "(-alpha*alpha*t*t*t*"+u1+")"
    dt_u0 = "("+u0+" + t*alpha*(x[0]*"+cos0+"*"+sin1+" + x[1]*"+sin0+"*"+cos1+"))"
    dt_u1 = "("+u1+" - t*alpha*(x[0]*"+sin0+"*"+cos1+" + x[1]*"+cos0+"*"+sin1+"))"
    d0_p = "(beta*t*exp(beta*t*x[0]))"
    d1_p = "(beta*t*exp(beta*t*x[1]))"

    u_ex = Expression(("t*"+u0, "t*"+u1), alpha=alpha, t=0)
    p_ex = Expression(("exp(beta*t*x[0])+exp(beta*t*x[1])"), beta=beta, t=0)
    f = Expression(( dt_u0+" - "+d00_u0+" + "+d0_p, dt_u1+" - "+d11_u1+" + "+d1_p), alpha=alpha, beta=beta, t=0)

    hmax = []
    u_err_norms = []
    p_err_norms = []
    for refine in range(2,3+refines):
        n_gridpoints = 2**refine
        mesh = UnitSquareMesh(n_gridpoints,n_gridpoints)
        boundaries = MeshFunction('size_t', mesh, mesh.topology().dim()-1)
        class Boundary(SubDomain):
            def inside(self, x, on_boundary):
                return on_boundary
        boundaries.set_all(0)
        Boundary().mark(boundaries, 1)
        dbcs = {1: u_ex}

        sol = solve_stokes(mesh,
                u_init = u_ex,
                f = f,
                lagrange_mult = True,
                boundaries = boundaries,
                dbcs = dbcs,
                expressions = [u_ex, p_ex],
                scale_dt = 0.2,
                linsolver = 'petsc',
                tend = 1,
                u_file = File("results/eoc2d_%02d_velocity.pvd" % refine),
                p_file = File("results/eoc2d_%02d_pressure.pvd" % refine),
                u_ex = u_ex,
                p_ex = p_ex,
                u_err_file = File("results/eoc2d_%02d_velocity_error.pvd" % refine),
                p_err_file = File("results/eoc2d_%02d_pressure_error.pvd" % refine)
                )
        hmax.append(mesh.hmax())
        u_err_norms.append( max(sol['u_err_norms']) )
        p_err_norms.append( max(sol['p_err_norms']) )

        print('max(u_err_norms):', max(sol['u_err_norms']))
        print('max(p_err_norms):', max(sol['p_err_norms']))
    hmax = np.array(hmax)
    u_err_norms = np.array(u_err_norms)
    p_err_norms = np.array(p_err_norms)

    u_eoc = np.log(u_err_norms[1:]/u_err_norms[:-1]) / np.log(hmax[1:]/hmax[:-1])
    p_eoc = np.log(p_err_norms[1:]/p_err_norms[:-1]) / np.log(hmax[1:]/hmax[:-1])

    pp.loglog(hmax, u_err_norms)
    pp.loglog(hmax, p_err_norms)
    pp.show()

def get_csr_matrix(A):
    '''get csr matrix from dolfin without copying data

    cf. http://code.google.com/p/pyamg/source/browse/branches/2.0.x/Examples/DolfinFormulation/demo.py
    '''
    (row,col,data) = A.data()
    return csr_matrix( (data,intc(col),intc(row)), shape=(A.size(0),A.size(1)) )

def getLinearOperator(A):
    '''construct a linear operator for easy application in a Krylov subspace method

    In a Krylov subspace method we only need the application of a linear operator
    to a vector or a block and this function returns a scipy.sparse.linalg.LinearOperator 
    that just does this.
    '''
    def matvec(v):
        vvec = Vector(A.size(1))
        vvec.set_local(v.reshape(v.shape[0]))
        resvec = Vector(A.size(0))
        A.mult(vvec, resvec)
        return resvec.array()
    return LinearOperator( (A.size(0), A.size(1)), matvec=matvec )

def solve_stokes(mesh,
                 u_init = Constant(0.),
                 f = Constant(0.),
                 lagrange_mult = False, # use if you solve a pure Dirichlet problem (for velocity)
                 boundaries = None,
                 dbcs = {},
                 nbcs = {},
                 expressions = [],
                 t0 = 0.0,
                 tend = 1.0,
                 scale_dt = 1.0,
                 linsolver = "krypy",
                 linsolver_params = {},
                 n_defl = 0,
                 u_file = None,
                 p_file = None,
                 u_err_file = None,
                 p_err_file = None,
                 u_ex = None,
                 p_ex = None
                 ):

    if boundaries is None:
        boundaries = MeshFunction('uint', mesh, mesh.topology().dim()-1)
        boundaries.set_all(0)

    if not dbcs and not nbcs:
        raise ValueError('Dirichlet or Neumann boundary conditions have to be specified (both possible)!')

    hmin = mesh.hmin()
    hmax = mesh.hmax()

    # keep a list of all expressions that need the current time
    expressions = list(expressions)
    expressions.append(f)
    expressions.extend(dbcs.values())
    expressions.extend(nbcs.values())
    if u_ex is not None:
        expressions.append(u_ex)
    if p_ex is not None:
        expressions.append(p_ex)
    # Set time in ALL THE expressions.
    # TODO this breaks if any of the expressions has no .t available. Fix this.
    def set_time(expressions, t):
        for expr in expressions:
            # TODO Well, well. If any of the expressions has a Sum(), in which
            #      one component has the parameter 't', that parameter is not
            #      going to get set. With hasattr(), this fails silently,
            #      otherwise an exception would be raised. This is something
            #      that needs to be fixed in any case.
            if hasattr(expr, 't'):
                expr.t = t

    # Define function spaces
    V = VectorFunctionSpace(mesh, "CG", 2)
    Q = FunctionSpace(mesh, "CG", 1)
    function_spaces = [V,Q]
    if lagrange_mult:
        L = FunctionSpace(mesh, "R", 0)
        function_spaces.append(L)
    W = MixedFunctionSpace(function_spaces)
    # The solution
    w = Function(W)

    # get dof mappings of subspaces
    Vdofs = W.sub(0).collapse(mesh)[1].values()
    Qdofs = W.sub(1).collapse(mesh)[1].values()
    n_dofs = len(Vdofs) + len(Qdofs)
    if lagrange_mult:
        Ldofs = W.sub(2).collapse(mesh)[1].values()
        n_dofs += len(Ldofs)

    t = t0
    set_time(expressions, t)
    dt = scale_dt * mesh.hmax()

    print('Solve with n_dofs=%d, dt=%e, hmin/hmax=%e.'
            % (n_dofs, dt, mesh.hmin()/mesh.hmax()))

    # Initial value
    u_old = Function(V)
    u_old.interpolate(u_init)
    if u_file is not None:
        u_file << u_old
    if p_file is not None:
        pass
        #TODO
        #p_file << ???

    # for initial vector of iterative method
    w0 = Function(W)
    w0.vector().zero()

    # deflation vectors
    Z = np.zeros( (n_dofs,0) )
    AZ = np.zeros( (n_dofs,0) )
    Proj = None

    # Define variational problem
    if lagrange_mult:
        (u, p, lam) = TrialFunctions(W)
        (v, q, l) = TestFunctions(W)
    else:
        (u, p) = TrialFunctions(W)
        (v, q) = TestFunctions(W)
    ds = Measure('ds')[boundaries]
    
    dbc = [DirichletBC(W.sub(0), bc, boundaries, tag) for tag, bc in dbcs.items()]
    Avar = inner(u,v)*dx + dt*(inner(grad(u), grad(v))*dx - div(v)*p*dx - q*div(u)*dx)
    if lagrange_mult:
        Avar += dt*(lam*q*dx + p*l*dx)

    # variational problem for preconditioner
    Mvar = inner(u,v)*dx + dt*inner(grad(u), grad(v))*dx + p*q*dx
    if lagrange_mult:
        Mvar += lam*l*dx
    Nvar = inner(grad(p),grad(q))*dx
    Mprec = None

    if u_ex is not None:
        u_err_norms = []
    if p_ex is not None:
        p_err_norms = []
    while t<tend:
        t += dt
        set_time(expressions, t)
        print(t)

        # update right hand side for implicit Euler
        bvar = inner(u_old,v)*dx + dt*inner(f, v)*dx
        if p_ex is not None and lagrange_mult:
            bvar += dt*p_ex*l*dx
        # incorporate Neumann boundary conditions into right hand side
        for tag, bc in nbcs.items():
            bvar += dt*bc*v*ds(tag)

        # solve the linear system
        if linsolver in ["petsc", "lu", "gmres"]:
            solve(Avar == bvar, w, dbc, solver_parameters = {"linear_solver": linsolver})
        elif linsolver=="krypy":
            A, b = assemble_system(Avar, bvar, dbc,
                  #exterior_facet_domains = boundaries
                  )

            # use initial guess that satisfies boundary conditions
            #w0.vector().zero()
            for bc in dbc:
                bc.apply(w0.vector())
            x0 = w0.vector().array().reshape((w0.vector().size(),1))

            A = get_csr_matrix(A)
            b = b.data().reshape((b.size(),1))

            # build preconditioner 
            # cf. "Fast iterative solvers for discrete Stokes equations", 
            # Peters, Reichelt, Reusken 2005
            if Mprec is None:
                M, _ = assemble_system(Mvar, bvar, dbc,
                        exterior_facet_domains=boundaries)
                M = get_csr_matrix(M)
                MV = M[Vdofs,:][:,Vdofs]
                MQ = M[Qdofs,:][:,Qdofs]
                if lagrange_mult:
                    ML = M[Ldofs,:][:,Ldofs]

                N, _ = assemble_system(Nvar, bvar, dbc,
                        exterior_facet_domains=boundaries)
                N = get_csr_matrix(N)
                NQ = N[Qdofs,:][:,Qdofs]

#                solver_diagnostics(MV,
#                       fname='solver_diagnostic_MV',
#                       definiteness='positive',
#                       symmetry='hermitian'
#                       )
#                solver_diagnostics(MQ,
#                       fname='solver_diagnostic_MQ',
#                       definiteness='positive',
#                       symmetry='hermitian'
#                       )
#                solver_diagnostics(NQ,
#                       fname='solver_diagnostic_NQ',
#                       definiteness='positive',
#                       symmetry='hermitian'
#                       )
#                return

                # pyamg is non-deterministic atm. fix it by setting the random seed
                # cf. https://code.google.com/p/pyamg/issues/detail?id=139
                np.random.seed(1337)

                MVamg = smoothed_aggregation_solver(MV, max_levels=25, max_coarse=50)
                MQamg = smoothed_aggregation_solver(MQ, max_levels=25, max_coarse=50)
                NQamg = smoothed_aggregation_solver(NQ, max_levels=25, max_coarse=50)
                amgtol = 1e-15
                amgmaxiter = 3

                def Prec_solve(x):
                    xV = x[Vdofs]
                    xQ = x[Qdofs]
                    if lagrange_mult:
                        xL = x[Ldofs]
                    ret = np.zeros(x.shape)
                    ret[Vdofs] = MVamg.solve(xV, maxiter=amgmaxiter, tol=amgtol).reshape(xV.shape)
                    if hmin**2 <= dt:
                        ret[Qdofs] =           MQamg.solve(xQ, maxiter=amgmaxiter, tol=amgtol).reshape(xQ.shape) \
                                   + (1/dt)   *NQamg.solve(xQ, maxiter=amgmaxiter, tol=amgtol).reshape(xQ.shape)
                    else:
                        ret[Qdofs] = (hmin**2/dt)*MQamg.solve(xQ, maxiter=amgmaxiter, tol=amgtol).reshape(xQ.shape) \
                                   + (1/dt)   *NQamg.solve(xQ, maxiter=amgmaxiter, tol=amgtol).reshape(xQ.shape)
                    if lagrange_mult:
                        ret[Ldofs] = xL
                    return ret
                Prec = LinearOperator(A.shape, Prec_solve)

            # prepare deflation vectors
            if Z.shape[1] > 0:
                #Z, _ = np.linalg.qr(Z)
                AZ = A*Z
                Proj, x0 = utils.get_projection(b, Z, AZ, x0)

            itsol = linsys.gmres(A, b, x0=x0, tol=1e-6, maxiter=150, Mr=Proj, M=Prec, return_basis = True)

            print("GMRES performed %d iterations with final res %e." % (len(itsol["relresvec"])-1, itsol["relresvec"][-1]) )
            w.vector().set_local(itsol["xk"])

            # extract deflation data
            if ('Vfull' in itsol) and ('Hfull' in itsol):
                if n_defl > 0:
                    ritz_vals, ritz_coeffs, ritz_res_norm = utils.ritzh(itsol['Vfull'], itsol['Hfull'], Z, AZ, A, M=Prec)
                    sorti = np.argsort(abs(ritz_vals))
                    selection = sorti[:n_defl]
                    nZ = Z.shape[1]
                    Z = np.dot(Z, ritz_coeffs[0:nZ, selection]) \
                      + np.dot(itsol['Vfull'][:,0:-1], ritz_coeffs[nZ:,selection])
                else:
                    Z = np.zeros( (n_dofs,0) )
        else:
            raise RuntimeError("Linear solver '%s' unknown." % linsolver)

        # Get sub-functions
        w0.assign(w)
        if lagrange_mult:
            u_new, p_new, lam_new = w.split()
        else:
            u_new, p_new = w.split()
        # degree=... is used in dolfin 1.0, newer versions use degree_rise=... (which is cleaner)
        if u_file is not None:
            u_file << u_new, t
        if p_file is not None:
            p_file << p_new, t

        if u_ex is not None:
            u_err_norms += [errornorm(u_ex, u_new)]
            if u_err_file is not None:
                u_err = Function(V)
                u_err.interpolate(u_ex)
                u_new_tmp = Function(V)
                u_new_tmp.assign(u_new)
                u_err.vector().axpy(-1.0, u_new_tmp.vector())
                u_err_file << u_err
        if p_ex is not None:
            p_err_norms += [errornorm(p_ex, p_new)]
            if p_err_file is not None:
                p_err = Function(Q)
                p_err.interpolate(p_ex)
                p_new_tmp = Function(V)
                p_new_tmp.assign(p_new)
                p_err.vector().axpy(-1.0, p_new_tmp.vector())
                p_err_file << u_err

        u_old.assign(u_new)

    sol = {
            'u': u_new,
            'p': p_new,
          }
    if u_ex is not None:
        sol['u_err_norms'] = u_err_norms
    if p_ex is not None:
        sol['p_err_norms'] = p_err_norms
    print('norm(u_new) = %e' % norm(u_new))
    print('norm(p_new) = %e' % norm(p_new))
    if lagrange_mult:
        print('norm(lam_new) = %e' % norm(lam_new))

    return sol



if __name__ == '__main__':
    main()
