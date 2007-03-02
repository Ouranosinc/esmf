! $Id: ESMF_FortranWordsize.cpp,v 1.3 2007/03/02 22:37:21 theurich Exp $
!
! Earth System Modeling Framework
! Copyright 2002-2006, University Corporation for Atmospheric Research,
! Massachusetts Institute of Technology, Geophysical Fluid Dynamics
! Laboratory, University of Michigan, National Centers for Environmental
! Prediction, Los Alamos National Laboratory, Argonne National Laboratory,
! NASA Goddard Space Flight Center.
! Licensed under the University of Illinois-NCSA License.
!
!==============================================================================
^define ESMF_FILENAME "ESMF_FortranWordsize.F90"

!     ESMF FortranWordsize module
      module ESMF_FortranWordsizeMod

!==============================================================================
!
! This file contains wordsize functions that are automatically
!  generated from macros to handle the type/kind overloading.
!
!------------------------------------------------------------------------------
! INCLUDES
! < ignore blank lines below.  they are created by the files which
! define various macros. >
#include "ESMF_TypeKindMacros.hcppF90"
#include "ESMF_FortranWordsizeMacros.h"
^include "ESMF.h"
!------------------------------------------------------------------------------
! !USES:
     use ESMF_UtilTypesMod      
     use ESMF_LogErrMod

     implicit none

!------------------------------------------------------------------------------
! !PRIVATE TYPES:
      private

!------------------------------------------------------------------------------
! !PUBLIC FUNCTION:

      public ESMF_FortranWordsize

!------------------------------------------------------------------------------
^undef  ESMF_METHOD
^define ESMF_METHOD "ESMF_FortranWordsize"
!BOP
! !IROUTINE: ESMF_FortranWordsize -- Generic interface to find Fortran data sizes
!
! !INTERFACE:


    interface ESMF_FortranWordsize
!EOP

      ! < interfaces for each TK >
TypeKindTemplateInterfaceMacro(ESMF_FortranWordsize)

    end interface

    contains

!==============================================================================
!------------------------------------------------------------------------------

TypeKindTemplateDeclarationMacro(ESMF_FortranWordsize)

!! < end of automatically generated functions >
!------------------------------------------------------------------------------

!------------------------------------------------------------------------------

    end module ESMF_FortranWordsizeMod
