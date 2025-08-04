from rest_framework import serializers
from .models import Customer, Loan
from decimal import Decimal


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'customer_id', 'first_name', 'last_name', 'age', 
            'phone_number', 'monthly_income', 'approved_limit', 
            'current_debt', 'name'
        ]
        read_only_fields = ['customer_id', 'approved_limit', 'current_debt']

    def create(self, validated_data):
        # Calculate approved limit based on monthly income
        monthly_income = validated_data['monthly_income']
        approved_limit = round((36 * monthly_income) / 100000) * 100000
        validated_data['approved_limit'] = approved_limit
        return super().create(validated_data)


class LoanSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    customer = CustomerSerializer(read_only=True)
    repayments_left = serializers.ReadOnlyField()
    
    class Meta:
        model = Loan
        fields = [
            'loan_id', 'customer_id', 'customer', 'loan_amount', 
            'tenure', 'interest_rate', 'monthly_installment', 
            'emis_paid_on_time', 'start_date', 'end_date', 
            'status', 'repayments_left'
        ]
        read_only_fields = ['loan_id', 'monthly_installment', 'emis_paid_on_time', 'start_date', 'end_date', 'status']

    def create(self, validated_data):
        customer_id = validated_data.pop('customer_id')
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError(f"Customer with ID {customer_id} does not exist")
        
        validated_data['customer'] = customer
        return super().create(validated_data)


class RegisterCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']

    def create(self, validated_data):
        # Calculate approved limit based on monthly income
        monthly_income = validated_data['monthly_income']
        approved_limit = round((36 * monthly_income) / 100000) * 100000
        validated_data['approved_limit'] = approved_limit
        return super().create(validated_data)

    def to_representation(self, instance):
        return {
            'customer_id': instance.customer_id,
            'name': instance.name,
            'age': instance.age,
            'monthly_income': instance.monthly_income,
            'approved_limit': instance.approved_limit,
            'phone_number': instance.phone_number
        }


class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(min_value=1, max_value=120)

    def validate_customer_id(self, value):
        try:
            Customer.objects.get(customer_id=value)
        except Customer.DoesNotExist:
            raise serializers.ValidationError(f"Customer with ID {value} does not exist")
        return value


class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField(min_value=1, max_value=120)

    def validate_customer_id(self, value):
        try:
            Customer.objects.get(customer_id=value)
        except Customer.DoesNotExist:
            raise serializers.ValidationError(f"Customer with ID {value} does not exist")
        return value


class LoanDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = [
            'loan_id', 'customer', 'loan_amount', 'interest_rate', 
            'monthly_installment', 'tenure'
        ]

    def get_customer(self, obj):
        return {
            'id': obj.customer.customer_id,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name,
            'phone_number': obj.customer.phone_number,
            'age': obj.customer.age
        }


class CustomerLoanListSerializer(serializers.ModelSerializer):
    repayments_left = serializers.ReadOnlyField()
    
    class Meta:
        model = Loan
        fields = [
            'loan_id', 'loan_amount', 'interest_rate', 
            'monthly_installment', 'repayments_left'
        ] 