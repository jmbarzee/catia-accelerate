# Links

The honest state of public CATIA automation resources, as of late 2026.

## Official

- **V5Automation.chm**: ships with CATIA under `<install>\win_b64\code\bin\`. Also from
  Help > Automation Documentation. Not on the public web. The only complete reference.
  Known to omit members and carry stale signatures in places. Run `tools/extract_chm.py`.
- **CATIA V5 Automation student guide** (course code EDU_CAT_EN_VBA_AF): Dassault training
  material. Ask your CATIA administrator whether your company holds it.
- **Dassault Systèmes user communities** (3ds.com) require a customer login.

## Open source

- **pycatia**: Python wrapper over the V5 COM API. https://github.com/evereux/pycatia,
  docs at https://pycatia.readthedocs.io. Alpha-quality but the docs are a browsable mirror
  of the object model that works even if you never write Python.
- There is **no reputable open-source CATScript or CATVBA macro library**. What exists is
  forum attachments, paid packs, and PDF mirror sites of questionable provenance.
  Write small macros, commit them, and share them internally.

## Forums worth searching

- Eng-Tips CATIA forum: https://www.eng-tips.com (search "CATScript" plus your member name)
- GrabCAD CATIA groups and questions
- Visiativ / myCAD forum (French, lots of V5 macro knowledge): https://forum.mycad.visiativ.com
- COE (CATIA Operators Exchange) archives, if your company is a member

## Large assemblies

- EDS Technologies, Large Assembly Management in CATIA V5: https://edstechnologies.com/?p=7420
- PTC Windchill docs on the CGR cache (the mechanism is CATIA's, the page is clear):
  https://support.ptc.com/help/windchill/plus/r13.1.2.0/pt_BR/Windchill_Help_Center/WWGMforCatiaV5/WGMCATIAV5AdvTechCGRCache.html

## Books

- "CATIA V5 Macro Programming with Visual Basic Script" (Dieter Ziethen, Hanser). German
  original, English translation. The standard book. Buy it, do not download PDF mirrors.

## 3DEXPERIENCE (V6) users

Most of `quickref/` navigation and Part Design carries over. The large-assembly story is
different: Explore vs Edit mode, Volume Filter, and the data lives in the database.
Automation uses EKL and a different automation layer (CAA / 3DEXPERIENCE automation via
`CATIA.Application` still exists but the document model is `PLMNewService`-based).
This repo targets V5. A V6 branch would replace cards 03, 04, and the object model map.
