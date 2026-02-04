package com.sentinel.sentinel_core.repository;

import com.sentinel.sentinel_core.model.TenantMember;
import com.sentinel.sentinel_core.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface TenantMemberRepository extends JpaRepository<TenantMember, UUID> {
    List<TenantMember> findByUser(User user);
    Optional<TenantMember> findByUserIdAndTenantId(UUID userId, UUID tenantId);
}