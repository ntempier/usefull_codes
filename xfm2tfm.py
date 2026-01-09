import os


def _read_xfm_matrix(xfm_path):
    rows = []
    with open(xfm_path, "r") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            rows.append([float(p) for p in parts[:4]])
            if len(rows) == 4:
                break
    if len(rows) != 4:
        raise RuntimeError(f"XFM invalide (4x4 attendu): {xfm_path}")
    return rows


def _invert_affine(r, t):
    a, b, c = r[0]
    d, e, f = r[1]
    g, h, i = r[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-9:
        raise RuntimeError("Matrice singuliere, inversion impossible.")
    inv = [
        [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
        [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
        [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det],
    ]
    t_inv = [
        -(inv[0][0] * t[0] + inv[0][1] * t[1] + inv[0][2] * t[2]),
        -(inv[1][0] * t[0] + inv[1][1] * t[1] + inv[1][2] * t[2]),
        -(inv[2][0] * t[0] + inv[2][1] * t[1] + inv[2][2] * t[2]),
    ]
    return inv, t_inv


def _apply_lps_flip(r, t):
    # Convert RAS <-> LPS by flipping X and Y.
    s = [-1.0, -1.0, 1.0]
    sr = [[s[i] * r[i][j] for j in range(3)] for i in range(3)]
    r2 = [[sr[i][j] * s[j] for j in range(3)] for i in range(3)]
    t2 = [s[0] * t[0], s[1] * t[1], s[2] * t[2]]
    return r2, t2


def _write_tfm(tfm_path, r, t):
    params = [
        r[0][0],
        r[0][1],
        r[0][2],
        r[1][0],
        r[1][1],
        r[1][2],
        r[2][0],
        r[2][1],
        r[2][2],
        t[0],
        t[1],
        t[2],
    ]
    with open(tfm_path, "w") as handle:
        handle.write("#Insight Transform File V1.0\n")
        handle.write("#Transform 0\n")
        handle.write("Transform: AffineTransform_double_3_3\n")
        handle.write(
            "Parameters: " + " ".join(f"{v:.6f}" for v in params) + "\n"
        )
        handle.write("FixedParameters: 0 0 0\n")


def xfm_to_tfm(xfm_path, tfm_path=None):
    if not os.path.isfile(xfm_path):
        raise FileNotFoundError(f"XFM introuvable: {xfm_path}")

    if tfm_path is None:
        base, _ = os.path.splitext(xfm_path)
        tfm_path = base + ".tfm"

    m = _read_xfm_matrix(xfm_path)
    r = [m[0][:3], m[1][:3], m[2][:3]]
    t = [m[0][3], m[1][3], m[2][3]]

    r_inv, t_inv = _invert_affine(r, t)
    r_out, t_out = _apply_lps_flip(r_inv, t_inv)
    _write_tfm(tfm_path, r_out, t_out)
    return tfm_path
