#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 12 easy-Urdu tashreeh v4 chunks into jild-12.json.

Reads the 12 leaf chunk files listed in chunks-manifest-v4-jild12.json,
concatenates them in order 01 -> 12, derives start_page = min(pages)
where the field is absent, normalises page markers, validates, and
writes {"masail": [...]} to jild-12.json.

ORDER -- chunk order is the order:
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-12.json
  has ID order == concatenation order of the v4 leaf chunks (verified
  locally by the coordinator: all 338 ids match the v3 sequence exactly).
  Do NOT sort or reorder. Within each chunk, items keep file order.
  CHUNK_ORDER is the numeric range pattern (no lettered leaves this
  jild — v3 split files 10a/10b were combined into ONE leaf 10).

BOUNDARY DEDUP (6 masail — the Jild 10 masala-87 / Jild 11 pattern):
  the v3 chunk files overlap by one item at 6 boundaries; the merged
  v3 has each ONCE with combined pages + combined notes. Each boundary
  masala is written ONCE, in the EARLIER leaf, combining both halves'
  tashreeh into one flowing passage with ALL notes from both halves:
  masala-20 (leaf 01), masala-137 (leaf 05), masala-240-241 (leaf 07),
  masala-271 (leaf 09), masala-289 (leaf 10), masala-303 (leaf 10).
  The LATER leaf EXCLUDES the boundary masala. Leaf page ranges
  overlap at 5 shared pages (156, 371, 474, 563, 613 — consecutive
  items sharing a page), so per-leaf present pages sum to 593 while
  the merged file has 588 UNIQUE pages. Those are v3 ids, kept exactly
  — they are NOT merge renames.

NO RENAME QUIRK in Jild 12: the v3 merged file has 338 UNIQUE ids — the
  book numbers no masala twice in this jild (unlike Jild 5, which had
  two masail 263 and two masail 304, and Jild 6, which had two masail
  774). Chunk ids are used exactly as written; the merge asserts
  duplicate-free ids instead of renaming anything.
  NOTE: v3 has split files 10a/10b — the pair was combined into ONE
  leaf chunk 10 (32 items). Leaf 01 has only 59 pages present in
  pp.5-156 (big source gaps, pp.8-100 absent from the source DB).
  Leaf 11's first id is the page item jild12-p613 (NOT masala-304).
  Leaf 12 is maakhiz + zamima (48 items, 48 of the jild's 57 empty
  sawal). The combined-range id jild12-masala-240-241 is a v3 id,
  kept exactly.

START_PAGE: every one of the 12 v4 leaf chunks carries start_page ==
  min(pages) for all its items (verified by the coordinator). The
  derivation code below stays as a safety net; it is expected to
  derive 0 items.

MARKER NORMALISATION (the only text transformation): page markers, if
  present, are normalised to the single form [safha N] written with the
  Urdu word for page:
  - lenticular-bracket form (U+3010/U+3011 around the Urdu word for
    page + number) -> [safha N]
  - [short form] -> [safha N]
  - [safha N] stays as-is
  Applied to every string field of every item (jawab, sawal, title,
  notes). The 12 v4 chunks contain ZERO markers of any form (verified
  locally), so normalisation is expected to be a no-op here; the code
  stays so the merge is robust and the "none remain" assertions still
  run. No other text is touched and no markers are invented.
  NOTE: the literal lenticular-bracket characters are written here only
  as U+3010/U+3011 escapes, never as literal characters in this file.

VALIDATION (fails loudly on any violation):
  338 items; ID sequence EXACTLY == the v3 merged file's ID sequence
  (embedded below as V3_IDS, copied verbatim from
  ~/workspace/fatawa-app/content/tashreeh/jild-12.json); pages per item
  identical to v3 (embedded as V3_PAGES, same source, verified against
  the v3 file before pushing); 588 unique pages (min 5, max 688);
  volume_ids == {55}; start_page == min(pages) for every item (after
  derivation); zero empty tashreeh_jawab; no lenticular / short markers
  remain; first id jild12-p5, last id jild12-zamima-22.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild12.json"

# Concatenation order: chunk files 01 -> 18, in order.
CHUNK_ORDER = [f"jild-12-chunk-{n:02d}.json" for n in range(1, 13)]

EXPECTED_ITEMS = 338
EXPECTED_PAGES = 588
EXPECTED_MIN_PAGE = 5
EXPECTED_MAX_PAGE = 688
EXPECTED_VOLUME_IDS = {55}
EXPECTED_FIRST_ID = "jild12-p5"
EXPECTED_LAST_ID = "jild12-zamima-22"

# v3 ID sequence, verbatim from content/tashreeh/jild-12.json.
V3_IDS = ['jild12-p5', 'jild12-masala-1-2', 'jild12-masala-3', 'jild12-masala-4', 'jild12-masala-5', 'jild12-masala-6', 'jild12-masala-7', 'jild12-masala-8', 'jild12-masala-9', 'jild12-masala-10', 'jild12-masala-11', 'jild12-masala-12', 'jild12-masala-13', 'jild12-masala-14', 'jild12-masala-15', 'jild12-masala-16', 'jild12-masala-17', 'jild12-masala-18', 'jild12-masala-19', 'jild12-masala-20', 'jild12-masala-21', 'jild12-masala-22', 'jild12-masala-23', 'jild12-masala-24', 'jild12-masala-25', 'jild12-masala-26', 'jild12-masala-27', 'jild12-masala-28', 'jild12-masala-29', 'jild12-masala-30', 'jild12-masala-31-32', 'jild12-masala-33', 'jild12-masala-34', 'jild12-masala-35', 'jild12-masala-36', 'jild12-masala-37-42', 'jild12-masala-43', 'jild12-masala-44-45', 'jild12-masala-46-47', 'jild12-masala-48', 'jild12-masala-49', 'jild12-masala-50', 'jild12-masala-51', 'jild12-masala-52', 'jild12-masala-53', 'jild12-masala-54', 'jild12-masala-55', 'jild12-masala-56', 'jild12-masala-57', 'jild12-masala-58', 'jild12-masala-59', 'jild12-masala-60', 'jild12-masala-61', 'jild12-masala-62', 'jild12-masala-63', 'jild12-masala-64', 'jild12-masala-65-66', 'jild12-masala-67', 'jild12-masala-68-70', 'jild12-masala-71-72', 'jild12-masala-73', 'jild12-masala-74', 'jild12-masala-75', 'jild12-masala-76', 'jild12-masala-77', 'jild12-masala-78', 'jild12-fasl-awwal', 'jild12-masala-79', 'jild12-fasl-doom', 'jild12-masala-80-86', 'jild12-masala-87', 'jild12-masala-88', 'jild12-masala-89', 'jild12-masala-90', 'jild12-masala-91', 'jild12-masala-92-93', 'jild12-masala-94', 'jild12-masala-95', 'jild12-masala-96', 'jild12-masala-97', 'jild12-masala-98', 'jild12-masala-99', 'jild12-masala-100', 'jild12-masala-101-102', 'jild12-masala-103', 'jild12-masala-104', 'jild12-masala-105', 'jild12-masala-106', 'jild12-masala-107', 'jild12-masala-108', 'jild12-masala-109', 'jild12-masala-110', 'jild12-masala-111', 'jild12-masala-112', 'jild12-masala-113', 'jild12-masala-114', 'jild12-masala-115', 'jild12-masala-116-117', 'jild12-masala-118', 'jild12-masala-119-120', 'jild12-masala-121', 'jild12-masala-122', 'jild12-masala-123', 'jild12-masala-124', 'jild12-masala-125', 'jild12-masala-126', 'jild12-masala-127', 'jild12-masala-128', 'jild12-masala-129', 'jild12-masala-130', 'jild12-masala-131', 'jild12-masala-132', 'jild12-masala-133', 'jild12-masala-134', 'jild12-masala-135', 'jild12-masala-136', 'jild12-masala-137', 'jild12-masala-138', 'jild12-masala-139', 'jild12-masala-140', 'jild12-masala-141', 'jild12-masala-142', 'jild12-masala-143', 'jild12-masala-144', 'jild12-masala-145', 'jild12-masala-146', 'jild12-masala-147', 'jild12-masala-148', 'jild12-masala-149', 'jild12-masala-150', 'jild12-masala-151-152', 'jild12-masala-153', 'jild12-masala-154', 'jild12-masala-155', 'jild12-masala-156', 'jild12-masala-157', 'jild12-masala-158', 'jild12-masala-159', 'jild12-masala-160', 'jild12-masala-161-163', 'jild12-masala-164-166', 'jild12-masala-167', 'jild12-masala-168', 'jild12-masala-169', 'jild12-masala-170', 'jild12-masala-171-173', 'jild12-masala-174-180', 'jild12-masala-181', 'jild12-masala-182-183', 'jild12-masala-184', 'jild12-masala-185', 'jild12-masala-187', 'jild12-masala-188', 'jild12-masala-189', 'jild12-masala-190', 'jild12-masala-191', 'jild12-masala-192', 'jild12-masala-193', 'jild12-masala-194', 'jild12-masala-195', 'jild12-masala-196', 'jild12-masala-197', 'jild12-masala-198', 'jild12-masala-199', 'jild12-masala-200', 'jild12-masala-201', 'jild12-masala-202', 'jild12-masala-203', 'jild12-masala-204', 'jild12-masala-205', 'jild12-masala-206', 'jild12-masala-207', 'jild12-masala-208', 'jild12-masala-209', 'jild12-masala-210', 'jild12-masala-211', 'jild12-masala-212', 'jild12-masala-213', 'jild12-masala-214', 'jild12-masala-215', 'jild12-masala-216', 'jild12-masala-217', 'jild12-masala-218', 'jild12-masala-219', 'jild12-masala-220', 'jild12-masala-222', 'jild12-masala-223', 'jild12-masala-224', 'jild12-masala-225', 'jild12-masala-226', 'jild12-masala-227', 'jild12-masala-228-229', 'jild12-masala-230', 'jild12-masala-231', 'jild12-masala-232', 'jild12-masala-233', 'jild12-masala-234', 'jild12-masala-235', 'jild12-masala-236', 'jild12-masala-237', 'jild12-masala-238', 'jild12-masala-239', 'jild12-masala-240-241', 'jild12-masala-242', 'jild12-masala-243', 'jild12-masala-244', 'jild12-masala-245', 'jild12-masala-246', 'jild12-masala-247', 'jild12-masala-248', 'jild12-masala-249', 'jild12-masala-250-254', 'jild12-masala-255', 'jild12-masala-256', 'jild12-masala-257', 'jild12-masala-258', 'jild12-masala-259', 'jild12-masala-260', 'jild12-masala-261', 'jild12-masala-262', 'jild12-masala-263', 'jild12-masala-264', 'jild12-masala-265', 'jild12-masala-266', 'jild12-masala-267', 'jild12-masala-268', 'jild12-fehrist-alfaz-talaq', 'jild12-masala-269', 'jild12-masala-270', 'jild12-masala-271', 'jild12-masala-272', 'jild12-masala-273', 'jild12-masala-274', 'jild12-masala-275', 'jild12-masala-276', 'jild12-masala-277', 'jild12-masala-278', 'jild12-masala-279', 'jild12-masala-280', 'jild12-masala-281', 'jild12-masala-282', 'jild12-masala-283', 'jild12-p581', 'jild12-masala-285', 'jild12-masala-286', 'jild12-masala-287', 'jild12-masala-288', 'jild12-masala-289', 'jild12-masala-290', 'jild12-masala-291', 'jild12-masala-292', 'jild12-masala-293', 'jild12-masala-294', 'jild12-masala-295', 'jild12-masala-296', 'jild12-masala-297', 'jild12-masala-298', 'jild12-masala-299', 'jild12-masala-300', 'jild12-masala-301', 'jild12-masala-302', 'jild12-masala-303', 'jild12-p613', 'jild12-masala-304', 'jild12-masala-305', 'jild12-masala-306', 'jild12-masala-307', 'jild12-masala-308', 'jild12-masala-309', 'jild12-masala-310', 'jild12-masala-311', 'jild12-masala-312', 'jild12-masala-313', 'jild12-masala-314', 'jild12-masala-315', 'jild12-masala-316', 'jild12-masala-317', 'jild12-masala-318', 'jild12-masala-319', 'jild12-masala-320', 'jild12-p637', 'jild12-masala-321', 'jild12-masala-322', 'jild12-masala-323', 'jild12-masala-324', 'jild12-masala-325', 'jild12-masala-326', 'jild12-masala-327', 'jild12-masala-328', 'jild12-p656', 'jild12-maakhiz-01', 'jild12-maakhiz-02', 'jild12-maakhiz-03', 'jild12-maakhiz-04', 'jild12-maakhiz-05', 'jild12-maakhiz-06', 'jild12-maakhiz-07', 'jild12-maakhiz-08', 'jild12-maakhiz-09', 'jild12-maakhiz-10', 'jild12-maakhiz-11', 'jild12-maakhiz-12', 'jild12-maakhiz-13', 'jild12-maakhiz-14', 'jild12-maakhiz-15', 'jild12-maakhiz-16', 'jild12-maakhiz-17', 'jild12-maakhiz-18', 'jild12-maakhiz-19', 'jild12-maakhiz-20', 'jild12-maakhiz-21', 'jild12-maakhiz-22', 'jild12-maakhiz-23', 'jild12-maakhiz-24', 'jild12-maakhiz-25', 'jild12-maakhiz-26', 'jild12-zamima-01', 'jild12-zamima-02', 'jild12-zamima-03', 'jild12-zamima-04', 'jild12-zamima-05', 'jild12-zamima-06', 'jild12-zamima-07', 'jild12-zamima-08', 'jild12-zamima-09', 'jild12-zamima-10', 'jild12-zamima-11', 'jild12-zamima-12', 'jild12-zamima-13', 'jild12-zamima-14', 'jild12-zamima-15', 'jild12-zamima-16', 'jild12-zamima-17', 'jild12-zamima-18', 'jild12-zamima-19', 'jild12-zamima-20', 'jild12-zamima-21', 'jild12-zamima-22']

# v3 pages per item id, verbatim from content/tashreeh/jild-12.json.
V3_PAGES = {
"jild12-p5": [5, 6, 7],
"jild12-masala-1-2": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121],
"jild12-masala-3": [121, 122],
"jild12-masala-4": [122, 123],
"jild12-masala-5": [123, 124, 125],
"jild12-masala-6": [125, 126],
"jild12-masala-7": [126, 127, 128, 129, 130],
"jild12-masala-8": [130, 131, 132],
"jild12-masala-9": [132, 133],
"jild12-masala-10": [133, 134, 135],
"jild12-masala-11": [135, 136, 137],
"jild12-masala-12": [137, 138],
"jild12-masala-13": [138],
"jild12-masala-14": [138, 139],
"jild12-masala-15": [139, 140, 141],
"jild12-masala-16": [141, 142],
"jild12-masala-17": [141, 142, 143],
"jild12-masala-18": [143, 144],
"jild12-masala-19": [144, 145],
"jild12-masala-20": [145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156],
"jild12-masala-21": [156, 157],
"jild12-masala-22": [157, 158],
"jild12-masala-23": [158],
"jild12-masala-24": [159, 160],
"jild12-masala-25": [160, 161],
"jild12-masala-26": [161, 162],
"jild12-masala-27": [162, 163, 164],
"jild12-masala-28": [164, 165],
"jild12-masala-29": [165],
"jild12-masala-30": [165, 166],
"jild12-masala-31-32": [166, 167],
"jild12-masala-33": [167, 168],
"jild12-masala-34": [168, 169],
"jild12-masala-35": [169, 170],
"jild12-masala-36": [170, 171, 172],
"jild12-masala-37-42": [172, 173],
"jild12-masala-43": [173, 174],
"jild12-masala-44-45": [174],
"jild12-masala-46-47": [175, 176],
"jild12-masala-48": [176],
"jild12-masala-49": [176],
"jild12-masala-50": [177],
"jild12-masala-51": [177],
"jild12-masala-52": [177, 178],
"jild12-masala-53": [178],
"jild12-masala-54": [179],
"jild12-masala-55": [179, 180],
"jild12-masala-56": [180],
"jild12-masala-57": [180, 181],
"jild12-masala-58": [181],
"jild12-masala-59": [181, 182],
"jild12-masala-60": [182, 183],
"jild12-masala-61": [183],
"jild12-masala-62": [184],
"jild12-masala-63": [184, 185],
"jild12-masala-64": [185, 186, 187, 188, 189],
"jild12-masala-65-66": [189, 190, 191],
"jild12-masala-67": [191, 192, 193],
"jild12-masala-68-70": [193, 194, 195],
"jild12-masala-71-72": [195, 196],
"jild12-masala-73": [197, 198, 199],
"jild12-masala-74": [199],
"jild12-masala-75": [201],
"jild12-masala-76": [202],
"jild12-masala-77": [202, 203, 204, 205, 206, 207, 208, 209, 210],
"jild12-masala-78": [210],
"jild12-fasl-awwal": [211],
"jild12-masala-79": [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226],
"jild12-fasl-doom": [227],
"jild12-masala-80-86": [227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250],
"jild12-masala-87": [250, 251, 252, 253, 254],
"jild12-masala-88": [254, 255],
"jild12-masala-89": [256],
"jild12-masala-90": [256, 257, 258],
"jild12-masala-91": [258, 259],
"jild12-masala-92-93": [259],
"jild12-masala-94": [259, 260],
"jild12-masala-95": [261],
"jild12-masala-96": [262],
"jild12-masala-97": [262, 263],
"jild12-masala-98": [264],
"jild12-masala-99": [265],
"jild12-masala-100": [265, 266],
"jild12-masala-101-102": [267, 268],
"jild12-masala-103": [269, 270],
"jild12-masala-104": [270, 271],
"jild12-masala-105": [273, 274, 275],
"jild12-masala-106": [275, 276],
"jild12-masala-107": [276, 277, 278, 279],
"jild12-masala-108": [279, 280],
"jild12-masala-109": [280],
"jild12-masala-110": [281, 282, 283, 284],
"jild12-masala-111": [284, 285, 286],
"jild12-masala-112": [287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319],
"jild12-masala-113": [321, 322],
"jild12-masala-114": [323, 324],
"jild12-masala-115": [324, 325],
"jild12-masala-116-117": [325, 326, 327],
"jild12-masala-118": [327, 328],
"jild12-masala-119-120": [328, 329, 330, 331, 332, 333, 334, 335],
"jild12-masala-121": [335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358],
"jild12-masala-122": [358],
"jild12-masala-123": [358, 359, 360],
"jild12-masala-124": [360],
"jild12-masala-125": [361],
"jild12-masala-126": [361, 362],
"jild12-masala-127": [362],
"jild12-masala-128": [362, 363],
"jild12-masala-129": [363, 364, 365],
"jild12-masala-130": [366],
"jild12-masala-131": [366, 367],
"jild12-masala-132": [367],
"jild12-masala-133": [367, 368],
"jild12-masala-134": [368],
"jild12-masala-135": [368, 369],
"jild12-masala-136": [369],
"jild12-masala-137": [369, 370, 371],
"jild12-masala-138": [371],
"jild12-masala-139": [371, 372, 373],
"jild12-masala-140": [373, 374],
"jild12-masala-141": [374],
"jild12-masala-142": [374, 375],
"jild12-masala-143": [375, 376],
"jild12-masala-144": [376],
"jild12-masala-145": [376, 377, 378],
"jild12-masala-146": [378],
"jild12-masala-147": [379],
"jild12-masala-148": [379, 380],
"jild12-masala-149": [381, 382],
"jild12-masala-150": [382],
"jild12-masala-151-152": [382, 383],
"jild12-masala-153": [383],
"jild12-masala-154": [383, 384],
"jild12-masala-155": [384, 385],
"jild12-masala-156": [385, 386],
"jild12-masala-157": [386],
"jild12-masala-158": [387],
"jild12-masala-159": [387, 388],
"jild12-masala-160": [388],
"jild12-masala-161-163": [388, 389, 390],
"jild12-masala-164-166": [390, 391],
"jild12-masala-167": [391, 392],
"jild12-masala-168": [392, 393, 394],
"jild12-masala-169": [394, 395],
"jild12-masala-170": [395, 396],
"jild12-masala-171-173": [396, 397],
"jild12-masala-174-180": [397, 398, 399],
"jild12-masala-181": [400, 401],
"jild12-masala-182-183": [401, 402, 403],
"jild12-masala-184": [404],
"jild12-masala-185": [404, 405, 406, 407],
"jild12-masala-187": [407, 408, 409],
"jild12-masala-188": [409],
"jild12-masala-189": [409, 410, 411, 412],
"jild12-masala-190": [412, 413],
"jild12-masala-191": [413, 414, 415, 416],
"jild12-masala-192": [416, 417],
"jild12-masala-193": [417, 418],
"jild12-masala-194": [418, 419],
"jild12-masala-195": [419],
"jild12-masala-196": [419, 420],
"jild12-masala-197": [421],
"jild12-masala-198": [421, 422],
"jild12-masala-199": [422, 423],
"jild12-masala-200": [423, 424],
"jild12-masala-201": [424, 425, 426],
"jild12-masala-202": [426, 427],
"jild12-masala-203": [427, 428],
"jild12-masala-204": [428, 429, 430],
"jild12-masala-205": [430, 431],
"jild12-masala-206": [431, 432],
"jild12-masala-207": [432, 433],
"jild12-masala-208": [433, 434, 435, 436],
"jild12-masala-209": [436, 437, 438, 439],
"jild12-masala-210": [439, 440, 441, 442, 443],
"jild12-masala-211": [443],
"jild12-masala-212": [443, 444],
"jild12-masala-213": [444, 445],
"jild12-masala-214": [445, 446],
"jild12-masala-215": [447, 448],
"jild12-masala-216": [448, 449, 450],
"jild12-masala-217": [450, 451],
"jild12-masala-218": [451, 452],
"jild12-masala-219": [452],
"jild12-masala-220": [452, 453],
"jild12-masala-222": [453, 454],
"jild12-masala-223": [454, 455],
"jild12-masala-224": [455],
"jild12-masala-225": [456],
"jild12-masala-226": [456, 457],
"jild12-masala-227": [458],
"jild12-masala-228-229": [458, 459],
"jild12-masala-230": [460],
"jild12-masala-231": [460, 461],
"jild12-masala-232": [461, 462],
"jild12-masala-233": [462, 463],
"jild12-masala-234": [463, 464],
"jild12-masala-235": [464],
"jild12-masala-236": [465],
"jild12-masala-237": [466],
"jild12-masala-238": [466, 467],
"jild12-masala-239": [467, 468, 469, 470],
"jild12-masala-240-241": [470, 471, 472, 473, 474],
"jild12-masala-242": [474, 475],
"jild12-masala-243": [475, 476],
"jild12-masala-244": [476],
"jild12-masala-245": [476, 477],
"jild12-masala-246": [477, 478, 479],
"jild12-masala-247": [479, 480, 481],
"jild12-masala-248": [481, 482, 483],
"jild12-masala-249": [483, 484],
"jild12-masala-250-254": [484, 485, 486, 487],
"jild12-masala-255": [487, 488],
"jild12-masala-256": [488, 489, 490, 491, 492, 493, 494, 495],
"jild12-masala-257": [495],
"jild12-masala-258": [495, 496],
"jild12-masala-259": [496, 497, 498, 499, 500, 501, 502],
"jild12-masala-260": [502, 503],
"jild12-masala-261": [503, 504, 505, 506],
"jild12-masala-262": [506, 507, 508],
"jild12-masala-263": [508],
"jild12-masala-264": [508, 509],
"jild12-masala-265": [509, 510],
"jild12-masala-266": [510, 511],
"jild12-masala-267": [511, 512],
"jild12-masala-268": [513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556],
"jild12-fehrist-alfaz-talaq": [556, 557, 558],
"jild12-masala-269": [559],
"jild12-masala-270": [560, 561],
"jild12-masala-271": [561, 562, 563],
"jild12-masala-272": [563, 564, 565, 566, 567, 568],
"jild12-masala-273": [568, 569],
"jild12-masala-274": [569, 570],
"jild12-masala-275": [570],
"jild12-masala-276": [570, 571],
"jild12-masala-277": [571, 572],
"jild12-masala-278": [572],
"jild12-masala-279": [572, 573, 574],
"jild12-masala-280": [574, 575],
"jild12-masala-281": [575],
"jild12-masala-282": [575, 576, 577, 578],
"jild12-masala-283": [579, 580, 581],
"jild12-p581": [581, 582],
"jild12-masala-285": [582, 583, 584],
"jild12-masala-286": [584, 585],
"jild12-masala-287": [585, 586],
"jild12-masala-288": [586, 587],
"jild12-masala-289": [587, 588, 589],
"jild12-masala-290": [589, 590, 591, 592],
"jild12-masala-291": [592, 593],
"jild12-masala-292": [593, 594, 595],
"jild12-masala-293": [595, 596],
"jild12-masala-294": [596, 597, 598],
"jild12-masala-295": [599, 600, 601, 602],
"jild12-masala-296": [602, 603, 604],
"jild12-masala-297": [604, 605],
"jild12-masala-298": [605, 606],
"jild12-masala-299": [606, 607],
"jild12-masala-300": [607, 608],
"jild12-masala-301": [608],
"jild12-masala-302": [608, 609],
"jild12-masala-303": [609, 610, 611, 612, 613],
"jild12-p613": [613, 614],
"jild12-masala-304": [614, 615],
"jild12-masala-305": [615, 616, 617],
"jild12-masala-306": [617],
"jild12-masala-307": [617, 618, 619],
"jild12-masala-308": [620, 621, 622],
"jild12-masala-309": [622, 623],
"jild12-masala-310": [623, 624],
"jild12-masala-311": [624, 625],
"jild12-masala-312": [625],
"jild12-masala-313": [625, 626],
"jild12-masala-314": [626],
"jild12-masala-315": [626, 627],
"jild12-masala-316": [627, 628],
"jild12-masala-317": [628],
"jild12-masala-318": [629],
"jild12-masala-319": [629, 630],
"jild12-masala-320": [630, 631, 632, 633, 634, 635, 636],
"jild12-p637": [637],
"jild12-masala-321": [637, 638, 639],
"jild12-masala-322": [639, 640, 641, 642],
"jild12-masala-323": [642, 643],
"jild12-masala-324": [643, 644, 645, 646],
"jild12-masala-325": [646, 647, 648, 649, 650, 651, 652],
"jild12-masala-326": [653, 654],
"jild12-masala-327": [654, 655],
"jild12-masala-328": [655, 656],
"jild12-p656": [656],
"jild12-maakhiz-01": [657, 658, 659],
"jild12-maakhiz-02": [659],
"jild12-maakhiz-03": [659, 660, 661],
"jild12-maakhiz-04": [661],
"jild12-maakhiz-05": [661, 662],
"jild12-maakhiz-06": [662, 663],
"jild12-maakhiz-07": [663, 664],
"jild12-maakhiz-08": [664],
"jild12-maakhiz-09": [664],
"jild12-maakhiz-10": [664, 665],
"jild12-maakhiz-11": [665, 666],
"jild12-maakhiz-12": [666],
"jild12-maakhiz-13": [667, 668, 669],
"jild12-maakhiz-14": [669],
"jild12-maakhiz-15": [669],
"jild12-maakhiz-16": [669, 670],
"jild12-maakhiz-17": [670],
"jild12-maakhiz-18": [670, 671, 672],
"jild12-maakhiz-19": [672],
"jild12-maakhiz-20": [673, 674],
"jild12-maakhiz-21": [674, 675],
"jild12-maakhiz-22": [675, 676, 677, 678, 679],
"jild12-maakhiz-23": [679],
"jild12-maakhiz-24": [679],
"jild12-maakhiz-25": [680],
"jild12-maakhiz-26": [680],
"jild12-zamima-01": [681, 682],
"jild12-zamima-02": [682],
"jild12-zamima-03": [682],
"jild12-zamima-04": [682, 683],
"jild12-zamima-05": [683],
"jild12-zamima-06": [683],
"jild12-zamima-07": [683],
"jild12-zamima-08": [683],
"jild12-zamima-09": [684],
"jild12-zamima-10": [684],
"jild12-zamima-11": [684],
"jild12-zamima-12": [684, 685],
"jild12-zamima-13": [685],
"jild12-zamima-14": [685],
"jild12-zamima-15": [685],
"jild12-zamima-16": [685],
"jild12-zamima-17": [686],
"jild12-zamima-18": [686],
"jild12-zamima-19": [686, 687],
"jild12-zamima-20": [687, 688],
"jild12-zamima-21": [688],
"jild12-zamima-22": [688],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 12, f"expected 12 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (none expected: all chunks carry start_page).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        all_items.extend(items)

    # NO RENAME QUIRK in Jild 12: the v3 merged file has 338 UNIQUE
    # ids — the book numbers no masala twice in this jild. Chunk ids
    # are used exactly as written.
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS before validation: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )
    print("renames applied: [] (no duplicate masala numbers in Jild 12)")

    print(f"concatenated: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert not empty, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-12.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-12.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
