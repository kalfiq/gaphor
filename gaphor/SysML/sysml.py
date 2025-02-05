# This file is generated by coder.py. DO NOT EDIT!
# ruff: noqa: F401, E402, F811
# fmt: off

from __future__ import annotations

from decimal import Decimal as UnlimitedNatural

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



def _directed_relationship_property_path_target_source(type):
    return lambda self: [
        element.targetContext
        for element in self.model.select(type)
        if element.sourceContext is self and element.targetContext
    ]

from gaphor.UML.uml import NamedElement
class AbstractRequirement(NamedElement):
    derived: derived[AbstractRequirement]
    derivedFrom: derived[AbstractRequirement]
    externalId: _attribute[str] = _attribute("externalId", str)
    master: derived[AbstractRequirement]
    refinedBy: derived[NamedElement]
    satisfiedBy: derived[NamedElement]
    text: _attribute[str] = _attribute("text", str)
    tracedTo: derived[NamedElement]
    verifiedBy: derived[NamedElement]


from gaphor.UML.uml import Class as _Class
class Requirement(AbstractRequirement, _Class):
    pass


from gaphor.UML.uml import DirectedRelationship
class DirectedRelationshipPropertyPath(DirectedRelationship):
    sourceContext: relation_one[Classifier]
    sourcePropertyPath: relation_many[Property]
    targetContext: relation_one[Classifier]
    targetPropertyPath: relation_many[Property]


from gaphor.UML.uml import Dependency
class Trace(Dependency, DirectedRelationshipPropertyPath):
    pass


class Copy(Trace):
    pass


class Verify(Trace):
    pass


class DeriveReqt(Trace):
    pass


class Satisfy(Trace):
    pass


from gaphor.UML.uml import Behavior
class TestCase(Behavior):
    pass


class Block(_Class):
    isEncapsulated: _attribute[bool] = _attribute("isEncapsulated", bool, default=False)


from gaphor.UML.uml import Property
class ConnectorProperty(Property):
    connector: relation_one[Connector]


class ParticipantProperty(Property):
    end_: relation_one[Property]


class DistributedProperty(Property):
    pass


from gaphor.UML.uml import DataType
class ValueType(DataType):
    quantityKind: relation_one[InstanceSpecification]
    unit: relation_one[InstanceSpecification]


from gaphor.UML.uml import InstanceSpecification
from gaphor.UML.uml import Element
class ElementPropertyPath(Element):
    propertyPath: relation_many[Property]


from gaphor.UML.uml import Connector
class BindingConnector(Connector):
    pass


from gaphor.UML.uml import ConnectorEnd
class NestedConnectorEnd(ConnectorEnd, ElementPropertyPath):
    pass


from gaphor.UML.uml import Classifier
class PropertySpecificType(Classifier):
    pass


class EndPathMultiplicity(Property):
    pass


class BoundReference(EndPathMultiplicity):
    bindingPath: relation_many[Property]
    boundend: relation_many[ConnectorEnd]


class AdjuntProperty(Property):
    principal: relation_one[Element]


from gaphor.UML.uml import Port
class ProxyPort(Port):
    pass


class FullPort(Port):
    pass


class FlowProperty(Property):
    direction = _enumeration("direction", ("in", "inout", "out"), "in")


class InterfaceBlock(Block):
    pass


from gaphor.UML.uml import InvocationAction
from gaphor.UML.uml import Trigger
from gaphor.UML.uml import AddStructuralFeatureValueAction
class InvocationOnNestedPortAction(ElementPropertyPath, InvocationAction):
    onNestedPort: relation_many[Port]


class TriggerOnNestedPort(ElementPropertyPath, Trigger):
    onNestedPort: relation_many[Port]


class AddFlowPropertyValueOnNestedPortAction(AddStructuralFeatureValueAction, ElementPropertyPath):
    pass


from gaphor.UML.uml import ChangeEvent
class ChangeSructuralFeatureEvent(ChangeEvent):
    structuralFeature: relation_one[StructuralFeature]


from gaphor.UML.uml import StructuralFeature
from gaphor.UML.uml import AcceptEventAction
class AcceptChangeStructuralFeatureEventAction(AcceptEventAction):
    pass


from gaphor.UML.uml import Feature
class DirectedFeature(Feature):
    featureDirection = _enumeration("featureDirection", ("provided", "providedRequired", "required"), "provided")


from gaphor.UML.uml import Generalization
class Conform(Generalization):
    pass


class View(_Class):
    stakeholder: relation_many[Stakeholder]
    viewpoint: relation_one[Viewpoint]


class Viewpoint(_Class):
    concernList: relation_many[Comment]
    language: _attribute[str] = _attribute("language", str)
    method: relation_many[Behavior]
    presentation: _attribute[str] = _attribute("presentation", str)
    purpose: _attribute[str] = _attribute("purpose", str)
    stakeholder: relation_many[Stakeholder]


class Stakeholder(Classifier):
    concernList: relation_many[Comment]


class Expose(Dependency):
    pass


from gaphor.UML.uml import Comment
class Rationale(Comment):
    pass


class Problem(Comment):
    pass


class ElementGroup(Comment):
    member: relation_many[Element]
    name: _attribute[str] = _attribute("name", str)
    orderedMember: relation_many[Element]


class ConstraintBlock(Block):
    pass


from gaphor.UML.uml import Parameter
from gaphor.UML.uml import ActivityEdge
from gaphor.UML.uml import ParameterSet
class Optional(Parameter):
    pass


class Rate(ActivityEdge, Parameter):
    rate: relation_many[InstanceSpecification]


class Probability(ActivityEdge, ParameterSet):
    probability: _attribute[str] = _attribute("probability", str)


class Continuous(Rate):
    pass


class Discrete(Rate):
    pass


from gaphor.UML.uml import Operation
from gaphor.UML.uml import ObjectNode
class ControlOperator(Behavior):
    pass


class NoBuffer(ObjectNode):
    pass


class Overwrite(ObjectNode):
    pass


from gaphor.UML.uml import Abstraction
class Allocate(Abstraction, DirectedRelationshipPropertyPath):
    pass


from gaphor.UML.uml import ActivityPartition
class AllocateActivityPartition(ActivityPartition):
    pass


class Refine(Dependency, DirectedRelationshipPropertyPath):
    pass


class Tagged(Property):
    nonunique: _attribute[bool] = _attribute("nonunique", bool)
    ordered: _attribute[bool] = _attribute("ordered", bool)
    subsets: _attribute[str] = _attribute("subsets", str)


class ClassifierBehaviorProperty(Property):
    pass


from gaphor.UML.uml import InformationFlow
class ItemFlow(InformationFlow):
    itemProperty: relation_one[Property]


from gaphor.UML.uml import Diagram
from gaphor.UML.uml import Class
class SysMLDiagram(Diagram):
    pass


class StructureDiagram(SysMLDiagram):
    pass


class BehaviorDiagram(SysMLDiagram):
    pass


class BlockDefinitionDiagram(StructureDiagram):
    diagramType: _attribute[str] = _attribute("diagramType", str, default="bdd")


class InternalBlockDiagram(StructureDiagram):
    diagramType: _attribute[str] = _attribute("diagramType", str, default="ibd")


class ParametricDiagram(InternalBlockDiagram):
    diagramType: _attribute[str] = _attribute("diagramType", str, default="par")


class PackageDiagram(StructureDiagram):
    diagramType: _attribute[str] = _attribute("diagramType", str, default="pkg")


class RequirementDiagram(SysMLDiagram):
    diagramType: _attribute[str] = _attribute("diagramType", str, default="req")


class ActivityDiagram(BehaviorDiagram):
    diagramType: _attribute[str] = _attribute("diagramType", str, default="act")


class SequenceDiagram(BehaviorDiagram):
    diagramType: _attribute[str] = _attribute("diagramType", str, default="sd")


class StateMachineDiagram(BehaviorDiagram):
    diagramType: _attribute[str] = _attribute("diagramType", str, default="stm")


class UseCaseDiagram(BehaviorDiagram):
    diagramType: _attribute[str] = _attribute("diagramType", str, default="uc")



# 23: override AbstractRequirement.derived: derived[AbstractRequirement]

AbstractRequirement.derived = derived("derived", AbstractRequirement, 0, "*",
    _directed_relationship_property_path_target_source(DeriveReqt))

# 28: override AbstractRequirement.derivedFrom: derived[AbstractRequirement]

AbstractRequirement.derivedFrom = derived("derivedFrom", AbstractRequirement, 0, "*", lambda self: [
    element.sourceContext
    for element in self.model.select(DeriveReqt)
    if element.sourceContext and element.targetContext is self
])

# 36: override AbstractRequirement.master: derived[AbstractRequirement]

AbstractRequirement.master = derived("master", AbstractRequirement, 0, "*",
    _directed_relationship_property_path_target_source(Copy))

# 41: override AbstractRequirement.refinedBy: derived[NamedElement]

AbstractRequirement.refinedBy = derived("refinedBy", NamedElement, 0, "*",
    _directed_relationship_property_path_target_source(Refine))

# 46: override AbstractRequirement.satisfiedBy: derived[NamedElement]

AbstractRequirement.satisfiedBy = derived("satisfiedBy", NamedElement, 0, "*",
    _directed_relationship_property_path_target_source(Satisfy))

# 51: override AbstractRequirement.tracedTo: derived[NamedElement]

AbstractRequirement.tracedTo = derived("tracedTo", NamedElement, 0, "*",
    _directed_relationship_property_path_target_source(Trace))

# 56: override AbstractRequirement.verifiedBy: derived[NamedElement]

AbstractRequirement.verifiedBy = derived("verifiedBy", NamedElement, 0, "*",
    _directed_relationship_property_path_target_source(Verify))

DirectedRelationshipPropertyPath.sourcePropertyPath = association("sourcePropertyPath", Property)
DirectedRelationshipPropertyPath.targetPropertyPath = association("targetPropertyPath", Property)
DirectedRelationshipPropertyPath.targetContext = association("targetContext", Classifier, upper=1, opposite="targetDirectedRelationshipPropertyPath_")
DirectedRelationshipPropertyPath.sourceContext = association("sourceContext", Classifier, upper=1)
Element.owner.add(DirectedRelationshipPropertyPath.targetContext)  # type: ignore[attr-defined]
Property.itemFlow = association("itemFlow", ItemFlow, upper=1, opposite="itemProperty")
Element.owner.add(Property.itemFlow)  # type: ignore[attr-defined]
ConnectorProperty.connector = association("connector", Connector, upper=1, composite=True)
ParticipantProperty.end_ = association("end_", Property, upper=1, composite=True)
ValueType.unit = association("unit", InstanceSpecification, upper=1)
ValueType.quantityKind = association("quantityKind", InstanceSpecification, upper=1)
ElementPropertyPath.propertyPath = association("propertyPath", Property, lower=1)
Classifier.targetDirectedRelationshipPropertyPath_ = association("targetDirectedRelationshipPropertyPath_", DirectedRelationshipPropertyPath, composite=True, opposite="targetContext")
Element.ownedElement.add(Classifier.targetDirectedRelationshipPropertyPath_)  # type: ignore[attr-defined]
BoundReference.boundend = association("boundend", ConnectorEnd, composite=True)
BoundReference.bindingPath = derivedunion("bindingPath", Property, lower=1)
AdjuntProperty.principal = association("principal", Element, upper=1)
InvocationOnNestedPortAction.onNestedPort = association("onNestedPort", Port, lower=1)
TriggerOnNestedPort.onNestedPort = association("onNestedPort", Port, lower=1)
ChangeSructuralFeatureEvent.structuralFeature = association("structuralFeature", StructuralFeature, upper=1)
View.stakeholder = derivedunion("stakeholder", Stakeholder)
View.viewpoint = derivedunion("viewpoint", Viewpoint, upper=1)
Viewpoint.concernList = association("concernList", Comment, composite=True)
Viewpoint.method = derivedunion("method", Behavior)
Viewpoint.stakeholder = association("stakeholder", Stakeholder, composite=True)
Stakeholder.concernList = association("concernList", Comment, composite=True)
ElementGroup.member = derivedunion("member", Element)
ElementGroup.orderedMember = association("orderedMember", Element, composite=True)
Rate.rate = association("rate", InstanceSpecification, composite=True)
ItemFlow.itemProperty = association("itemProperty", Property, upper=1, composite=True, opposite="itemFlow")
Element.ownedElement.add(ItemFlow.itemProperty)  # type: ignore[attr-defined]
