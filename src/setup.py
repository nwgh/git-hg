import os

config = {}

def __extract_name_email(info, type_):
    val = ' '.join(v.split(' ')[:-2])
    angle = val.find('<')
    if angle > -1:
        config['GIT_%s_NAME' % type_] = val[:angle - 1]
        config['GIT_%s_EMAIL' % type_] = val[angle + 1:-1]
    else:
        config['GIT_%s_NAME' % type_] = val

for k, v in os.environ.iteritems():
    if k == 'PY_GIT_CONFIG':
        cfgs = v.split('\n')
        for cfg in cfgs:
            var, val = cfg.split('=', 1)
            if val == 'true':
                val = True
            elif val == 'false':
                val = False
            else:
                try:
                    val = int(val)
                except:
                    pass
            config[var] = val
    elif k == 'PY_GIT_COMMITTER_IDENT':
        __extract_name_email(v, 'COMMITTER')
    elif k == 'PY_GIT_AUTHOR_IDENT':
        __extract_name_email(v, 'AUTHOR')
    elif k.startswith('PY_GIT_'):
        config[k[3:]] = v

if 'GIT_DIR' in config and not os.path.isabs(config['GIT_DIR']):
    git_dir = os.path.join(config['GIT_TOPLEVEL'], config['GIT_DIR'])
    config['GIT_DIR'] = os.path.abspath(git_dir)
