
"""
    Take a time series of water levels and return the wind effect,
    defined as the difference between observed and calculated (harmonic)
    level.

    Parameters
    -------
    time: time in datetime format
    h: water level
    sol, optional: utide output Bunch. A specific Utide object
    *args, **kwargs: arguments for optional run of Utide

    Returns
    -------
    h_astr, arraylike: calculated astronomical tide
    s, arraylike: calculated wind effect for every time in the set
    s_mean, s_min, s_max, float: mean, minimum and maximum setup
        in the set

    Issues
    --------
    None
 
    References
    --------
    Codiga, Daniel. (2011). Unified tidal analysis and 
        prediction using the UTide Matlab functions. 10.13140/RG.2.1.3761.2008
    
    Pugh, D. and P. Woodworth - Sea level science;
        Cambridge University Press, 2014
    """