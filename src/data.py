"""Strict parser: never silently replace absent feature tokens with zero."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GASES = {1: 'Ethanol', 2: 'Ethylene', 3: 'Ammonia', 4: 'Acetaldehyde', 5: 'Acetone', 6: 'Toluene'}
FEATURES = [f'f{i:03d}' for i in range(1, 129)]
KINDS = ['delta_R', 'normalized_R', 'EMA_rise_0.001', 'EMA_rise_0.01', 'EMA_rise_0.1',
         'EMA_decay_0.001', 'EMA_decay_0.01', 'EMA_decay_0.1']

def feature_label(index):
    return f'f{index:03d}: S{(index-1)//8+1} {KINDS[(index-1)%8]}'

def read_config(path=None):
    path = Path(path) if path else ROOT / 'config.json'
    config = json.loads(path.read_text(encoding='utf-8'))
    directory = Path(config['data_dir'])
    config['data_dir'] = str(directory if directory.is_absolute() else path.parent / directory)
    return config

def parse_line(line, n_features=128):
    tokens = line.split()
    if not tokens:
        raise ValueError('Blank data row')
    try:
        label = int(tokens[0])
    except ValueError as exc:
        raise ValueError('Expected integer gas label, without concentration field') from exc
    if label not in GASES:
        raise ValueError(f'Unknown label: {label}')
    if len(tokens) != n_features + 1:
        raise ValueError(f'Expected {n_features} explicit features, got {len(tokens)-1}')
    values, indices = [], []
    for token in tokens[1:]:
        try:
            key, value = token.split(':')
            indices.append(int(key))
            values.append(float(value))
        except (ValueError, TypeError) as exc:
            raise ValueError(f'Malformed index:value token: {token}') from exc
    if indices != list(range(1, n_features+1)):
        raise ValueError('Feature indices must appear exactly once in order 1..128')
    return label, values

def load_dataset(config):
    rows, records = [], []
    for batch in range(1, 11):
        path = Path(config['data_dir']) / f'batch{batch}.dat'
        if not path.is_file():
            raise FileNotFoundError(f'Missing required batch: {path}')
        payload = path.read_bytes()
        lines = payload.decode('utf-8').splitlines()
        batch_rows = []
        for number, line in enumerate(lines, 1):
            try:
                label, values = parse_line(line, config['n_features'])
            except ValueError as exc:
                raise ValueError(f'{path.name}:{number}: {exc}') from exc
            batch_rows.append([batch, number, label, *values])
        if not batch_rows:
            raise ValueError(f'Empty batch file: {path}')
        array = np.array([row[3:] for row in batch_rows])
        labels = np.array([row[2] for row in batch_rows])
        records.append(dict(batch=batch, file=path.name, exists=True, bytes=len(payload),
                            sha256=hashlib.sha256(payload).hexdigest(), samples=len(lines),
                            features=config['n_features'], missing_nan=int(np.isnan(array).sum()),
                            infinite=int(np.isinf(array).sum()),
                            label_runs=int(1+np.count_nonzero(labels[1:] != labels[:-1])),
                            labels_nondecreasing=bool(np.all(labels[1:] >= labels[:-1])),
                            tabs=payload.count(b'\t'), spaces=payload.count(b' '),
                            format='whitespace-delimited LIBSVM; label + index:value; explicit 1..128'))
        rows.extend(batch_rows)
    frame = pd.DataFrame(rows, columns=['batch', 'source_line', 'gas', *FEATURES])
    frame['row_id'] = [f'b{b:02d}_r{n:05d}' for b, n in zip(frame.batch, frame.source_line)]
    return frame, pd.DataFrame(records)

def duplicate_summary(frame):
    hashes = pd.util.hash_pandas_object(frame[FEATURES], index=False).astype(str)
    # Hashes identify split groups; exact value comparisons compute reported duplicate counts.
    exact = frame.duplicated(FEATURES, keep=False)
    repeated = frame.duplicated(FEATURES, keep='first')
    labeled = frame.duplicated(['gas', *FEATURES], keep='first')
    groups = frame.groupby(FEATURES, sort=False, dropna=False).agg(
        rows=('gas', 'size'), labels=('gas', 'nunique'), batches=('batch', 'nunique'))
    return hashes, dict(feature_duplicate_extra=int(repeated.sum()),
                        feature_duplicate_rows=int(exact.sum()),
                        labeled_duplicate_extra=int(labeled.sum()),
                        conflicting_label_groups=int(((groups.rows > 1) & (groups.labels > 1)).sum()),
                        cross_batch_duplicate_groups=int(((groups.rows > 1) & (groups.batches > 1)).sum()))
