from rest_framework import serializers
from apps.emergency.models import Emergency, EmergencyStep
from apps.emergency.constants import EMERGENCY_STEP, EmergencyType

class EmergencySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyStep
        fields = "__all__"

    def to_internal_value(self, data):
        self.assign_step(data)
        return super().to_internal_value(data)
    
    def assign_step(self, data):
        last_step = EmergencyStep.objects.all().order_by("-id").first()
        if last_step:
            data["step_num"] = last_step.step_num + 1
        else:
            data["step_num"] = 1

    def validate(self, attrs):
        self.validate_duplicate_step(attrs)
        self.validate_default_step(attrs)
        self.validate_default_completed_step(attrs)
        return super().validate(attrs)
    
    def validate_default_step(self, attrs):
        if attrs.get("is_default"):
            default_step = EmergencyStep.objects.filter(is_default=True)
            if self.instance:
                default_step = default_step.exclude(id=self.instance.id)

            if default_step.exists():
                raise serializers.ValidationError(
                    {"is_default": "This default step already exists."}
                )
            
    def validate_default_completed_step(self, attrs):
        if attrs.get("is_completed"):
            default_step = EmergencyStep.objects.filter(is_completed=True)
            if self.instance:
                default_step = default_step.exclude(id=self.instance.id)

            if default_step.exists():
                raise serializers.ValidationError(
                    {"is_default": "This completed step already exists."}
                )

    def validate_duplicate_step(self, attrs):
        step = EmergencyStep.objects.filter(
            step_num=attrs.get("step_num"),
        )
        if self.instance:
            step = step.exclude(id=self.instance.id)
        if step.exists():
            raise serializers.ValidationError({"step": "This step already exists."})
        

class EmergencySerializer(serializers.ModelSerializer):
    emergency_type_name = serializers.CharField(source="emergency_type.name")

    class Meta:
        model = Emergency
        fields = "__all__"
