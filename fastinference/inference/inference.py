# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_inference.ipynb (unless otherwise specified).

__all__ = []

# Cell
from fastai2.vision.all import *
from fastai2.tabular.all import *

# Cell
@typedispatch
def _fully_decode(dl:TfmdDL, inps, outs):
    "Attempt to fully decode the `inp"
    inps = dl.decode(inps)
    dec = []
    for d in inps:
        for e in d:
            e = retain_type(e, typ=type(d))
            dec.append(e)
    outs.insert(len(outs), dec)
    return outs

# Cell
@typedispatch
def _fully_decode(dl:TabDataLoader, inps, outs):
    "Attempt to fully decode the `inp"
    for i in range(dl.n_inp):
        inps[i] = torch.cat(inps[i], dim=0)
    dec = dl.decode(inps)
    outs.insert(len(outs), dec)
    return outs

# Cell
def _decode_loss(vocab, dec_out, outs):
    i2c, dec2c = {}, []
    try:
        for i, vocab in enumerate(list(vocab)):
                i2c[i] = vocab
        for i, item in enumerate(dec_out):
            dec2c.append(i2c[int(item)])
        dec_out = dec2c
        outs.insert(0, dec_out)
    except:
        outs.insert(0, dec_out)
    return outs

# Cell
@patch
def get_preds(x:Learner, ds_idx=1, dl=None, raw_outs=False, decoded_loss=True, fully_decoded=False,
             **kwargs):
    "Get predictions with possible decoding"
    inps, outs, dec_out, raw,n_inp,is_multi = [], [], [], [], x.dls.n_inp,False
    if dl is None: dl = x.dls[ds_idx].new(shuffle=False, drop_last=False)
    if n_inp > 1:
        is_multi = True
        [inps.append([]) for _ in range(n_inp)]
    x.model.eval()
    for batch in dl:
        with torch.no_grad():
            if fully_decoded:
                if is_multi:
                    for i in range(n_inp):
                        inps[i].append(batch[i].cpu())
                else:
                    inps += batch[:n_inp]
            out = x.model(*batch[:n_inp])
            raw.append(out)
            if decoded_loss or fully_decoded:
                dec_out.append(x.loss_func.decodes(out))
    raw = torch.cat(raw, dim=0).cpu().numpy()
    if fully_decoded or decoded_loss:
        dec_out = torch.cat(dec_out, dim=0)
    if not raw_outs:
        try: outs.insert(0, x.loss_func.activation(tensor(raw)).numpy())
        except: outs.insert(0, dec_out)
    else:
        outs.insert(0, raw)
    if fully_decoded: outs = _fully_decode(x.dls[0], inps, outs)
    if decoded_loss: outs = _decode_loss(x.dls.vocab, dec_out, outs)
    return outs

# Cell
@patch
def predict(x:Learner, item, with_input=False, rm_type_tfms=None):
        dl = x.dls.test_dl([item], rm_type_tfms=rm_type_tfms, num_workers=0)
        res = x.get_preds(dl=dl, fully_decoded=True)
        if not with_input: res = res[:-1]
        return res

# Cell
@patch
def predict(x:TabularLearner, row, with_input=False, rm_type_tfms=None):
        tst_to = x.dls.valid_ds.new(pd.DataFrame(row).T)
        tst_to.process()
        tst_to.conts = tst_to.conts.astype(np.float32)
        dl = x.dls.valid.new(tst_to)
        res = x.get_preds(dl=dl, fully_decoded=True)
        if not with_input: res = res[:-1]
        return res