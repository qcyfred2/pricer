# -*- coding: utf-8 -*-
import yaml
from pricer.settings import BASE_DIR

with open(BASE_DIR+'/pricer/settings.yaml') as f:
    setting_str = f.read()
    f.close()
    setting_dict = yaml.load(setting_str)
