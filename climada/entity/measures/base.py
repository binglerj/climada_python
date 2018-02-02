"""
Define Action class and Measures.
"""

__all__ = ['Action', 'Measures']

import numpy as np

from climada.entity.loader import Loader
import climada.util.checker as check
from climada.entity.tag import Tag

class Measures(Loader):
    """Contains measures of type Measures.

    Attributes
    ----------
        tag (Taf): information about the source data
        _data (dict): cotains Action classes. It's not suppossed to be
            directly accessed. Use the class methods instead.
    """

    def __init__(self, file_name=None, description=None):
        """Fill values from file, if provided.

        Parameters
        ----------
            file_name (str, optional): name of the source file
            description (str, optional): description of the source data

        Raises
        ------
            ValueError

        Examples
        --------
            >>> act_1 = Action()
            >>> act_1.color_rgb = np.array([0.1529, 0.2510, 0.5451])
            >>> act_1.hazard_intensity = (1, 0)
            >>> act_1.mdd_impact = (1, 0)
            >>> act_1.paa_impact = (1, 0)
            >>> meas = Measures()
            >>> meas.data.append(act_1)
            >>> meas.tag.description = "my dummy measures."
            >>> meas.check()
            Fill measures with values and check consistency data.
        """
        self.tag = Tag(file_name, description)
        self._data = dict() # {Action()}

        # Load values from file_name if provided
        if file_name is not None:
            self.load(file_name, description)

    def add_action(self, action):
        """Add an Action.
        
        Parameters
        ----------
            action (Action): Action instance

        Raises
        ------
            ValueError
        """
        if not isinstance(action, Action):
            raise ValueError("Input value is not of type Action.")
        if action.name == 'NA':
            raise ValueError("Input Action's name not set.")
        self._data[action.name] = action

    def remove_action(self, name=None):
        """Remove Action with provided name. Delete all actions if no input
        name
        
        Parameters
        ----------
            action (Action): Action instance

        Raises
        ------
            ValueError
        """
        if name is not None:
            try:
                del self._data[name]
            except KeyError:
                raise ValueError('No Action with name %s.' % name)
        else:
            self._data = dict()

    def get_action(self, name=None):
        """Get Action with input name. Get all if no name provided.
        Parameters
        ----------
            name (str, optional): action type

        Returns
        -------
            Action (if name)
            list(Action) (if None)

        Raises
        ------
            ValueError    
        """
        if name is not None:
            try:
                return self._data[name]
            except KeyError:
                raise ValueError('No Action with name %s.' % name)
        else:
            return list(self._data.values())

    def get_names(self):
        """Get all Action names"""
        return list(self._data.keys())

    def num_action(self):
        """Get number of actions contained """
        return len(self._data.keys())

    def check(self):
        """ Override Loader check."""
        for act_name, act in self._data.items():
            if act_name != act.name:
                raise ValueError('Wrong Action.name: %s != %s' %\
                                (act_name, act.name))
            act.check()

class Action(object):
    """Contains the definition of one Action.

    Attributes
    ----------
        name (str): name of the action
        color_rgb (np.array): integer array of size 3. Gives color code of
            this measure in RGB
        cost (float): cost
        hazard_freq_cutoff (float): hazard frequency cutoff
        hazard_intensity (tuple): parameter a and b
        mdd_impact (tuple): parameter a and b of the impact over the mean
            damage (impact) degree
        paa_impact (tuple): parameter a and b of the impact over the
            percentage of affected assets (exposures)
        risk_transf_attach (float): risk transfer attach
        risk_transf_cover (float): risk transfer cover
    """

    def __init__(self):
        """ Empty initialization."""
        self.name = 'NA'
        self.color_rgb = np.array([0, 0, 0])
        self.cost = 0
        self.hazard_freq_cutoff = 0
#        self.hazard_event_set = 'NA'
        self.hazard_intensity = () # parameter a and b
        self.mdd_impact = () # parameter a and b
        self.paa_impact = () # parameter a and b
        self.risk_transf_attach = 0
        self.risk_transf_cover = 0

    def check(self):
        """ Check consistent instance data.

        Raises
        ------
            ValueError
        """
        check.size(3, self.color_rgb, 'Action.color_rgb')
        check.size(2, self.hazard_intensity, 'Action.hazard_intensity')
        check.size(2, self.mdd_impact, 'Action.mdd_impact')
        check.size(2, self.paa_impact, 'Action.paa_impact')
