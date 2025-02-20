"""The code generator for modeling languages.

This is the code generator for the models used by Gaphor.

In order to work with the code generator, a model should follow some conventions:

* `Profile` packages are only for profiles (excluded from generation)
* A stereotype `simpleAttribute` can be defined, which converts an association
  to a `str` attribute
* A stereotype attribute `subsets` can be defined in case an association is derived

The coder first write the class declarations, including attributes and enumerations.
After that, associations are filled in, including derived unions and redefines.

Notes:
* Enumerations are classes ending with "Kind" or "Sort".

The code generator works by reading a model and the models it depends on.
It defines classes, attributes, enumerations and associations. Class names
are considered unique.
"""

from __future__ import annotations

import argparse
import contextlib
import logging
import sys
import textwrap
from collections.abc import Iterable
from pathlib import Path

from gaphor import UML
from gaphor.codegen.override import Overrides
from gaphor.core.modeling import Base, ElementFactory
from gaphor.core.modeling.modelinglanguage import (
    CoreModelingLanguage,
    MockModelingLanguage,
    ModelingLanguage,
)
from gaphor.diagram.general.modelinglanguage import GeneralModelingLanguage
from gaphor.entrypoint import initialize
from gaphor.storage import storage
from gaphor.SysML.modelinglanguage import SysMLModelingLanguage
from gaphor.UML.modelinglanguage import UMLModelingLanguage

log = logging.getLogger(__name__)

header = textwrap.dedent(
    """\
    # This file is generated by coder.py. DO NOT EDIT!
    # {}: noqa: F401, E402, F811
    # fmt: off

    from __future__ import annotations

    from gaphor.core.modeling.properties import (
        association,
        attribute as _attribute,
        derived,
        derivedunion,
        enumeration as _enumeration,
        redefine,
        relation_many,
        relation_one,
    )

    from gaphor.core.modeling.base import UnlimitedNatural

    """.format("ruff")  # work around tooling triggers
)


def main(
    modelfile: str,
    supermodelfiles: list[tuple[str, str]] | None = None,
    overridesfile: str | None = None,
    outfile: str | None = None,
):
    logging.basicConfig()

    extra_langs = (
        [
            load_modeling_language(lang)
            for lang, _ in supermodelfiles
            if lang not in ("Core", "UML", "SysML")
        ]
        if supermodelfiles
        else []
    )
    modeling_language = MockModelingLanguage(
        *(
            [
                CoreModelingLanguage(),
                GeneralModelingLanguage(),
                UMLModelingLanguage(),
                SysMLModelingLanguage(),
            ]
            + extra_langs
        )
    )

    model = load_model(modelfile, modeling_language)
    super_models = (
        [
            (load_modeling_language(lang), load_model(f, modeling_language))
            for lang, f in supermodelfiles
        ]
        if supermodelfiles
        else []
    )
    overrides = Overrides(overridesfile) if overridesfile else None

    with (
        open(outfile, "w", encoding="utf-8")
        if outfile
        else contextlib.nullcontext(sys.stdout) as out
    ):
        for line in coder(model, super_models, overrides):
            print(line, file=out)


def load_model(modelfile: str, modeling_language: ModelingLanguage) -> ElementFactory:
    element_factory = ElementFactory()
    with open(modelfile, encoding="utf-8") as file_obj:
        storage.load(
            file_obj,
            element_factory,
            modeling_language,
        )

    resolve_attribute_type_values(element_factory)

    return element_factory


def load_modeling_language(lang) -> ModelingLanguage:
    return initialize("gaphor.modelinglanguages", [lang])[lang]


def coder(
    model: ElementFactory,
    super_models: list[tuple[ModelingLanguage, ElementFactory]],
    overrides: Overrides | None,
) -> Iterable[str]:
    classes = list(
        order_classes(
            c
            for c in model.select(UML.Class)
            if not is_enumeration(c)
            and not is_simple_type(c)
            and not is_in_profile(c)
            and not is_tilde_type(c)
        )
    )

    yield header
    if overrides and overrides.header:
        yield overrides.header

    already_imported = set()
    for c in classes:
        if overrides and overrides.has_override(c.name):
            yield overrides.get_override(c.name)
            continue

        if not any(bases(c)):
            element_type, cls = in_super_model(c.name, super_models)
            if element_type and cls:
                # always alias imported name
                line = f"from {element_type.__module__} import {element_type.__name__}"
                if len([t for t in classes if t.name == c.name]) > 1:
                    line += f" as _{c.name}"
                    c.name = f"_{c.name}"
                yield line
                already_imported.add(line)
                continue

        yield class_declaration(c)
        if properties := list(variables(c, overrides)):
            yield from (f"    {p}" for p in properties)
        else:
            yield "    pass"
        yield ""
        yield ""

    for c in classes:
        yield from operations(c, overrides)

    yield ""

    for c in classes:
        yield from associations(c, overrides)
        for line in subsets(c, super_models):
            if line.startswith("from "):
                if line not in already_imported:
                    yield line
                already_imported.add(line)
            else:
                yield line


def class_declaration(class_: UML.Class):
    base_classes = ", ".join(
        c.name for c in sorted(bases(class_), key=lambda c: c.name)
    )
    return f"class {class_.name}({base_classes}):"


def variables(class_: UML.Class, overrides: Overrides | None = None):
    if class_.ownedAttribute:
        a: UML.Property
        for a in sorted(class_.ownedAttribute, key=lambda a: a.name or ""):
            if is_extension_end(a):
                continue

            full_name = f"{class_.name}.{a.name}"
            if overrides and overrides.has_override(full_name):
                yield f"{a.name}: {overrides.get_type(full_name)}"
            elif a.isDerived and not a.type:
                log.warning(f"Derived attribute {full_name} has no implementation.")
            elif a.typeValue:
                yield f'{a.name}: _attribute[{a.typeValue}] = _attribute("{a.name}", {a.typeValue}{default_value(a)})'
            elif is_enumeration(a.type):
                assert isinstance(a.type, UML.Class)
                enum_values = ", ".join(f'"{e.name}"' for e in a.type.ownedAttribute)
                yield f'{a.name} = _enumeration("{a.name}", ({enum_values}), "{a.type.ownedAttribute[0].name}")'
            elif a.type:
                mult = (
                    "one"
                    if UML.recipes.get_multiplicity_upper_value_as_string(a) == "1"
                    else "many"
                )
                comment = "  # type: ignore[assignment]" if is_reassignment(a) else ""
                yield f"{a.name}: relation_{mult}[{a.type.name}]{comment}"
            else:
                assert isinstance(a.owner, Base)
                raise ValueError(
                    f"{a.name}: {a.type} can not be written; owner={a.owner.name}"  # type: ignore[attr-defined]
                )

    if class_.ownedOperation:
        for o in sorted(class_.ownedOperation, key=lambda a: a.name or ""):
            full_name = f"{class_.name}.{o.name}"
            if overrides and overrides.has_override(full_name):
                yield f"{o.name}: {overrides.get_type(full_name)}"
            else:
                log.warning(f"Operation {full_name} has no implementation")


def associations(
    c: UML.Class,
    overrides: Overrides | None = None,
):
    redefinitions = []
    for a in c.ownedAttribute:
        full_name = f"{c.name}.{a.name}"
        if overrides and overrides.has_override(full_name):
            yield overrides.get_override(full_name)
        elif (
            not a.type
            or is_simple_type(a.type)
            or is_enumeration(a.type)
            or is_extension_end(a)
        ):
            continue
        elif redefines(a):
            redefinitions.append(
                f'{full_name} = redefine({c.name}, "{a.name}", {a.type.name}, {redefines(a)}{opposite(a)})'
            )
        elif a.isDerived:
            yield f'{full_name} = derivedunion("{a.name}", {a.type.name}{lower(a)}{upper(a)})'
        elif not a.name:
            raise ValueError(f"Unnamed attribute: {full_name} ({a.association})")
        else:
            yield f'{full_name} = association("{a.name}", {a.type.name}{lower(a)}{upper(a)}{composite(a)}{opposite(a)})'

    yield from redefinitions


def subsets(
    c: UML.Class,
    super_models: list[tuple[ModelingLanguage, ElementFactory]],
):
    for a in c.ownedAttribute:
        if (
            not a.type
            or is_simple_type(a.type)
            or is_enumeration(a.type)
            or is_extension_end(a)
        ):
            continue
        for slot in a.appliedStereotype[:].slot:
            if slot.definingFeature.name != "subsets":
                continue

            full_name = f"{c.name}.{a.name}"
            raw_slot_value = UML.recipes.get_slot_value(slot)
            slotValue = raw_slot_value if isinstance(raw_slot_value, str) else ""
            for value in slotValue.split(","):
                element_type, d = attribute(c, value.strip(), super_models)
                if d:  # and d.isDerived:
                    if element_type:
                        # TODO: Use aliasses
                        yield f"from {element_type.__module__} import {d.owner.name}"  # type: ignore[attr-defined]
                    yield f"{d.owner.name}.{d.name}.add({full_name})  # type: ignore[attr-defined]"  # type: ignore[attr-defined]
                elif not d:
                    log.warning(
                        f"{full_name} wants to subset {value.strip()}, but it is not defined"
                    )
                else:
                    log.warning(
                        f"{full_name} wants to subset {value.strip()}, but it is not a derived union"
                    )


def operations(c: UML.Class, overrides: Overrides | None = None):
    if c.ownedOperation:
        for o in sorted(c.ownedOperation, key=lambda a: a.name or ""):
            full_name = f"{c.name}.{o.name}"
            if overrides and overrides.has_override(full_name):
                yield overrides.get_override(full_name)


def default_value(a) -> str:
    if a.defaultValue:
        if a.typeValue == "int":
            if isinstance(
                a.defaultValue,
                UML.LiteralString
                | UML.LiteralInteger
                | UML.LiteralUnlimitedNatural
                | UML.LiteralBoolean,
            ):
                defaultValue = UML.recipes.get_literal_value_as_string(a.defaultValue)
            else:
                defaultValue = a.defaultValue.title()
        elif a.typeValue == "str":
            if isinstance(
                a.defaultValue,
                UML.LiteralString
                | UML.LiteralInteger
                | UML.LiteralUnlimitedNatural
                | UML.LiteralBoolean,
            ):
                defaultValue = UML.recipes.get_literal_value_as_string(a.defaultValue)
            else:
                defaultValue = f'"{a.defaultValue}"'
        elif a.typeValue == "bool":
            if isinstance(a.defaultValue, UML.LiteralBoolean | UML.LiteralString):
                defaultValue = UML.recipes.get_literal_value_as_string(a.defaultValue)
            else:
                defaultValue = a.defaultValue
            if defaultValue == "true":
                defaultValue = "True"
            elif defaultValue == "false":
                defaultValue = "False"
        else:
            raise ValueError(
                f"Unknown default value type: {a.owner.name}.{a.name}: {a.typeValue} = {a.defaultValue}"
            )

        return f", default={defaultValue}"
    return ""


def lower(a):
    lowerValue = ""
    if isinstance(a.lowerValue, UML.LiteralInteger):
        if (
            a.lowerValue.value
            and a.lowerValue.value is not None
            and a.lowerValue.value != 0
        ):
            lowerValue = str(a.lowerValue.value)
    else:
        if a.lowerValue is not None and a.lowerValue != "0":
            lowerValue = a.lowerValue
    return "" if lowerValue == "" else f", lower={lowerValue}"


def upper(a):
    upperValue = ""
    if isinstance(a.upperValue, UML.LiteralUnlimitedNatural):
        if (
            a.upperValue.value
            and a.upperValue.value is not None
            and a.upperValue.value != "*"
        ):
            upperValue = str(int(a.upperValue.value))
    else:
        if a.upperValue is not None and a.upperValue != "*":
            upperValue = a.upperValue
    return "" if upperValue == "" else f", upper={upperValue}"


def composite(a):
    return ", composite=True" if a.aggregation == "composite" else ""


def opposite(a):
    return (
        f', opposite="{a.opposite.name}"'
        if a.opposite and a.opposite.name and a.opposite.class_
        else ""
    )


def order_classes(classes: Iterable[UML.Class]) -> Iterable[UML.Class]:
    seen_classes = set()

    def order(c):
        if c not in seen_classes:
            for b in bases(c):
                yield from order(b)
            yield c
            seen_classes.add(c)

    for c in classes:
        yield from order(c)


def bases(c: UML.Class) -> Iterable[UML.Class]:
    for g in c.generalization:
        assert isinstance(g.general, UML.Class)
        yield g.general

    for a in c.ownedAttribute:
        if a.association and a.name == "baseClass":
            yield a.association.ownedEnd.class_  # type: ignore[attr-defined]


def is_enumeration(c: UML.Type) -> bool:
    return c and c.name and (c.name.endswith("Kind") or c.name.endswith("Sort"))  # type: ignore[return-value]


def is_simple_type(c: UML.Type) -> bool:
    return any(
        s.name == "SimpleAttribute" for s in UML.recipes.get_applied_stereotypes(c)
    ) or any(is_simple_type(g.general) for g in c.generalization)  # type: ignore[attr-defined]


def is_tilde_type(c: UML.Type) -> bool:
    return c and c.name and c.name.startswith("~")  # type: ignore[return-value]


def is_extension_end(a: UML.Property):
    return isinstance(a.association, UML.Extension)


def is_reassignment(a: UML.Property) -> bool:
    def test(c: UML.Class):
        for attr in c.ownedAttribute:
            if attr.name == a.name:
                return True
        return any(test(base) for base in bases(c))

    return any(test(base) for base in bases(a.owner))  # type:ignore[arg-type]


def is_in_profile(c: UML.Class) -> bool:
    def test(p: UML.Package):
        return isinstance(p, UML.Profile) or (p.owningPackage and test(p.owningPackage))

    return test(c.owningPackage)  # type: ignore[no-any-return]


def is_in_toplevel_package(c: UML.Class, package_name: str) -> bool:
    def test(p: UML.Package):
        return (not p.owningPackage and p.name == package_name) or (
            p.owningPackage and test(p.owningPackage)
        )

    return test(c.owningPackage)  # type: ignore[no-any-return]


def redefines(a: UML.Property) -> str | None:
    # TODO: look up element name and add underscore if needed.
    # maybe resolve redefines before we start writing?
    # Redefine is the only one where
    return next(
        (
            UML.recipes.get_slot_value(slot)
            for slot in a.appliedStereotype[:].slot
            if slot.definingFeature.name == "redefines"
        ),
        None,
    )


def attribute(
    c: UML.Class, name: str, super_models: list[tuple[ModelingLanguage, ElementFactory]]
) -> tuple[type[Base] | None, UML.Property | None]:
    a: UML.Property | None
    for a in c.ownedAttribute:
        if a.name == name:
            return None, a

    for base in bases(c):
        element_type, a = attribute(base, name, super_models)
        if a:
            return element_type, a

    element_type, super_class = in_super_model(c.name, super_models)
    if super_class and c is not super_class:
        _, a = attribute(super_class, name, super_models)
        return element_type, a

    return None, None


def in_super_model(
    name: str, super_models: list[tuple[ModelingLanguage, ElementFactory]]
) -> tuple[type[Base], UML.Class] | tuple[None, None]:
    for modeling_language, factory in super_models:
        cls: UML.Class
        for cls in factory.select(  # type: ignore[assignment]
            lambda e: isinstance(e, UML.Class) and e.name == name
        ):
            if not (is_in_profile(cls) or is_enumeration(cls)):
                element_type = modeling_language.lookup_element(cls.name)
                assert element_type, (
                    f"Type {cls.name} found in model, but not in generated model"
                )
                return element_type, cls
    return None, None


def resolve_attribute_type_values(element_factory: ElementFactory) -> None:
    """Some model updates that are hard to do from Gaphor itself."""
    for prop in element_factory.select(UML.Property):
        if prop.typeValue in ("String", "str", "object"):
            prop.typeValue = "str"
        elif prop.typeValue in ("Boolean", "bool"):
            prop.typeValue = "bool"
        elif prop.typeValue in (
            "Integer",
            "int",
        ):
            prop.typeValue = "int"
        elif prop.typeValue == "UnlimitedNatural":
            pass
        elif c := next(
            element_factory.select(
                lambda e: isinstance(e, UML.Class) and e.name == prop.typeValue  # noqa: B023
            ),
            None,
        ):
            prop.type = c  # type: ignore[assignment]
            del prop.typeValue
            prop.aggregation = "composite"

        if prop.type and is_simple_type(prop.type):
            prop.typeValue = "str"
            del prop.type

        if not prop.type and prop.typeValue not in (
            "str",
            "int",
            "bool",
            "UnlimitedNatural",
            None,
        ):
            raise ValueError(f"Property value type {prop.typeValue} can not be found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("modelfile", type=Path, help="Gaphor model filename")
    parser.add_argument(
        "-o", dest="outfile", type=Path, help="Python data model filename"
    )
    parser.add_argument("-r", dest="overridesfile", type=Path, help="Override filename")
    parser.add_argument(
        "-s",
        dest="supermodelfiles",
        type=str,
        action="append",
        help="Reference to dependent model file (e.g. UML:models/UML.gaphor)",
    )

    args = parser.parse_args()
    supermodelfiles = (
        [s.split(":") for s in args.supermodelfiles] if args.supermodelfiles else []
    )

    main(args.modelfile, supermodelfiles, args.overridesfile, args.outfile)
