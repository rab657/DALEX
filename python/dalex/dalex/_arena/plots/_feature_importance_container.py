from dalex import Explainer
from .._plot_container import PlotContainer

class FeatureImportanceContainer(PlotContainer):
    info = {
        'name': "Variable Importance",
        'plotType': "FeatureImportance",
        'plotCategory': "Dataset Level",
        'requiredParams': ["model"]
    }
    options = {
        'N': { 'default': None, 'desc': 'Number of observations to use. None for all.' },
        'B': { 'default': 10, 'desc': 'Number of permutation rounds to perform each variable' }
    }
    def __init__(self, arena, model):
        super().__init__(
            arena,
            name=self.__class__.info.get('name'),
            plot_category=self.__class__.info.get('plotCategory'),
            plot_type=self.__class__.info.get('plotType'),
            plot_component='FeatureImportance'
        )
        if not isinstance(model, Explainer):
            raise Exception('Invalid Explainer argument')
        fi = model.model_parts(
            N=arena.get_option(self.plot_type, 'N'),
            B=arena.get_option(self.plot_type, 'B')
        ).permutation
        def q1(x):
            return x.quantile(0.25)
        def q3(x):
            return x.quantile(0.75)
        stats = fi.agg(['mean', 'max', 'min', q1, q3])
        full_model = stats.loc['mean', '_full_model_']
        stats = stats.drop(['_baseline_', '_full_model_'], axis=1) \
            .sort_values(by='mean', axis=1, ascending=False)
        self.data = {
            'base': full_model,
            'variables': stats.columns.tolist(),
            'dropout_loss': stats.loc['mean'].tolist(),
            'min': stats.loc['min'].tolist(),
            'max': stats.loc['max'].tolist(),
            'q1': stats.loc['q1'].tolist(),
            'q3': stats.loc['q3'].tolist()
        }
        self.params = {
            'model': model.label
        }
